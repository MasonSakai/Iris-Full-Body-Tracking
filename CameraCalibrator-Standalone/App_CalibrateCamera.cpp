#include "App_CalibrateCamera.h"
#include <opencv2/core.hpp>
#include <opencv2/imgcodecs.hpp>
#include <opencv2/highgui.hpp>
#include <opencv2/objdetect/charuco_detector.hpp>
#include <opencv2/calib3d.hpp>
#include "ConsoleMacros.h"
#include "util.h"
#include <opencv2/imgproc.hpp>

using cv::Mat;
using cv::Point2f;
using cv::Point3f;
using cv::Size;
using std::unique_ptr;

int charucoDictionaryID = cv::aruco::DICT_4X4_50;
float charucoSquareLength = 0.035142857142857f;
float charucoMarkerLength = 0.018f;

Size boardSize = { 5, 7 };

bool useFisheye = false;
int flag = 0;

static bool runCalibrationAndSave(CalibrationData& calibData, Size imageSize, Mat& cameraMatrix, Mat& distCoeffs, vector<vector<Point2f>> imagePoints);

static void GeneratePattern(cv::aruco::CharucoBoard board) {

	Mat boardImg;
	board.generateImage(boardSize * 100, boardImg);
	wstring path = getAppdata() + L"\\board_image.png";

	size_t len = (wcslen(path.c_str()) + 1) * sizeof(wchar_t);
	char* buffer = new char[len];
	size_t convertedSize;
	wcstombs_s(&convertedSize, buffer, len, path.c_str(), len);

	cv::imwrite(buffer, boardImg);

	delete[] buffer;
}

float delay = 0.1f;
int num = 150;

static void PrintCommands() {
	cout << CSI "4;0f" CSI "0J";
	cout << CUL("e") "xit, " CUL("g") "enerate calibration board, start " CUL("c") "alibration" << endl;
	cout << "(Commands are recieved via the Image Review window)";
}

void App_CalibrateCamera(const int cameraIndex, CalibrationData& calibData) {

	cv::aruco::Dictionary dictionary = cv::aruco::getPredefinedDictionary(charucoDictionaryID);
	cv::aruco::CharucoBoard board = cv::aruco::CharucoBoard(boardSize, charucoSquareLength, charucoMarkerLength, dictionary);
	cv::aruco::CharucoDetector detector(board);

	cout << CSI "4;0f" CSI "0J";

	int c;

	Mat cameraMatrix = Mat::eye(3, 3, CV_64F);
	Mat distCoeffs = Mat::zeros(8, 1, CV_64F);

	vector<int> markerIds;
	clock_t prevTimestamp = 0;

	vector<vector<Point2f>> imagePoints;
	Size imageSize;
	bool found;

	cv::VideoCapture cap;
	cap.open(cameraIndex, cv::CAP_ANY);
	cap.set(cv::CAP_PROP_FRAME_WIDTH, 1920);
	cap.set(cv::CAP_PROP_FRAME_HEIGHT, 1440);

	if (!cap.isOpened()) {
		cout << "ERROR! Unable to open camera\n";
		return;
	}

	Mat frame;
	cap.read(frame);
	cv::resize(frame, frame, { 640, 480 }, 0, 0, cv::INTER_LINEAR);
	cv::imshow("Image Review", frame);

	PrintCommands();

input:
	while ((c = cv::pollKey()) < 0) {
		cap.read(frame);
		cv::resize(frame, frame, { 640, 480 }, 0, 0, cv::INTER_LINEAR);
		cv::imshow("Image Review", frame);
	}
	switch (c)
	{
	case 'c': {
		prevTimestamp = clock();

		cout << CSI "4;0f" CSI "0J";
		cout << "Starting calibration, press escape to cancel" << endl << endl << CSP;

		for (;;) {

			cap.read(frame);
			imageSize = frame.size();
			//if (s.flipVertical) flip(view, view, 0);

			found = false;
			vector<Point2f> pointBuf;
			try {
				detector.detectBoard(frame, pointBuf, markerIds);
				found = pointBuf.size() == (size_t)((boardSize.height - 1) * (boardSize.width - 1));
			} catch (...) { }

			if (found) {
				if (clock() - prevTimestamp > delay * CLOCKS_PER_SEC) {
					imagePoints.push_back(pointBuf);
					prevTimestamp = clock();

					cout << "Number of recorded frames: " << imagePoints.size() << "/" << num << endl;
				}

				drawChessboardCorners(frame, cv::Size(boardSize.width - 1, boardSize.height - 1), Mat(pointBuf), found);
			}
			cv::resize(frame, frame, { 640, 480 }, 0, 0, cv::INTER_LINEAR);
			cv::imshow("Image Review", frame);

			if (imagePoints.size() >= num) {
				PrintCommands();
				cout << endl << endl;
				cout << "Number of recorded frames: " << imagePoints.size() << "/" << num << endl;
				if (runCalibrationAndSave(calibData, imageSize, cameraMatrix, distCoeffs, imagePoints)) { break; }
			}

			if (cv::pollKey() == 27) {

				PrintCommands();
				cout << endl << endl;
				cout << "Number of recorded frames: " << imagePoints.size() << "/" << num << endl;
				cout << COL("31") "Calibration Canceled" COLD;
				break;
			}

			cout << CRP;
		}

		imagePoints.clear();
		break;
	}
	case 'g': {
		GeneratePattern(board);
		break;
	}
	case 'e':
		goto exit;
	default:
		cout << "\x07" CRCD;
		break;
	}
	goto input;
exit:
	cv::destroyWindow("Image Review");
	return;
}


static double computeReprojectionErrors(const vector<vector<Point3f>>& objectPoints,
	const vector<vector<Point2f> >& imagePoints,
	const vector<Mat>& rvecs, const vector<Mat>& tvecs,
	const Mat& cameraMatrix, const Mat& distCoeffs,
	vector<float>& perViewErrors, bool fisheye)
{
	vector<Point2f> imagePoints2;
	size_t totalPoints = 0;
	double totalErr = 0, err;
	perViewErrors.resize(objectPoints.size());

	for (size_t i = 0; i < objectPoints.size(); ++i)
	{
		if (fisheye)
		{
			cv::fisheye::projectPoints(objectPoints[i], imagePoints2, rvecs[i], tvecs[i], cameraMatrix,
				distCoeffs);
		}
		else
		{
			projectPoints(objectPoints[i], rvecs[i], tvecs[i], cameraMatrix, distCoeffs, imagePoints2);
		}
		err = norm(imagePoints[i], imagePoints2, cv::NORM_L2);

		size_t n = objectPoints[i].size();
		perViewErrors[i] = (float)std::sqrt(err * err / n);
		totalErr += err * err;
		totalPoints += n;
	}

	return std::sqrt(totalErr / totalPoints);
}
static void calcBoardCornerPositions(Size boardSize, float squareSize, vector<Point3f>& corners)
{
	corners.clear();

	for (int i = 0; i < boardSize.height - 1; ++i) {
		for (int j = 0; j < boardSize.width - 1; ++j) {
			corners.push_back(Point3f(j * squareSize, i * squareSize, 0));
		}
	}
}

static bool runCalibration(Size& imageSize, Mat& cameraMatrix, Mat& distCoeffs,
	vector<vector<Point2f>> imagePoints, vector<Mat>& rvecs, vector<Mat>& tvecs,
	vector<float>& reprojErrs, double& totalAvgErr, vector<Point3f>& newObjPoints)
{
	float grid_width = charucoSquareLength * (boardSize.width - 2);

	//! [fixed_aspect]
	cameraMatrix = Mat::eye(3, 3, CV_64F);
	//! [fixed_aspect]
	if (useFisheye) {
		distCoeffs = Mat::zeros(4, 1, CV_64F);
	}
	else {
		distCoeffs = Mat::zeros(8, 1, CV_64F);
	}

	vector<vector<Point3f> > objectPoints(1);
	calcBoardCornerPositions(boardSize, charucoSquareLength, objectPoints[0]);
	objectPoints[0][boardSize.width - 2].x = objectPoints[0][0].x + grid_width;
	newObjPoints = objectPoints[0];

	objectPoints.resize(imagePoints.size(), objectPoints[0]);

	//Find intrinsic and extrinsic camera parameters
	double rms;

	if (useFisheye) {
		Mat _rvecs, _tvecs;
		rms = cv::fisheye::calibrate(objectPoints, imagePoints, imageSize, cameraMatrix, distCoeffs, _rvecs,
			_tvecs, flag);

		rvecs.reserve(_rvecs.rows);
		tvecs.reserve(_tvecs.rows);
		for (int i = 0; i < int(objectPoints.size()); i++) {
			rvecs.push_back(_rvecs.row(i));
			tvecs.push_back(_tvecs.row(i));
		}
	}
	else {
		rms = calibrateCameraRO(objectPoints, imagePoints, imageSize, -1,
			cameraMatrix, distCoeffs, rvecs, tvecs, newObjPoints,
			flag | cv::CALIB_USE_LU);
	}

	cout << "Re-projection error reported by calibrateCamera: " << rms << endl;

	bool ok = checkRange(cameraMatrix) && checkRange(distCoeffs);

	objectPoints.clear();
	objectPoints.resize(imagePoints.size(), newObjPoints);
	totalAvgErr = computeReprojectionErrors(objectPoints, imagePoints, rvecs, tvecs, cameraMatrix,
		distCoeffs, reprojErrs, useFisheye);

	return ok;
}

static void saveCameraParams(CalibrationData& calibData, Size& imageSize, Mat& cameraMatrix, Mat& distCoeffs,
	const vector<Mat>& rvecs, const vector<Mat>& tvecs,
	const vector<float>& reprojErrs, double totalAvgErr)
{

	time_t tm;
	time(&tm);
	struct tm t2;
	localtime_s(&t2, &tm);
	char buf[1024];
	strftime(buf, sizeof(buf), "%c", &t2);

	calibData.time = string(buf);

	calibData.nr_max = (int)std::max(rvecs.size(), reprojErrs.size());

	calibData.image_width = imageSize.width;
	calibData.image_height = imageSize.height;
	calibData.board_width = boardSize.width;
	calibData.board_height = boardSize.height;
	calibData.square_size = charucoSquareLength;
	calibData.marker_size = charucoMarkerLength;


	/*if (flag)
	{
		std::stringstream flagsStringStream;
		if (useFisheye)
		{
			flagsStringStream << "flags:"
				<< (flag & cv::fisheye::CALIB_FIX_SKEW ? " +fix_skew" : "")
				<< (flag & cv::fisheye::CALIB_FIX_K1 ? " +fix_k1" : "")
				<< (flag & cv::fisheye::CALIB_FIX_K2 ? " +fix_k2" : "")
				<< (flag & cv::fisheye::CALIB_FIX_K3 ? " +fix_k3" : "")
				<< (flag & cv::fisheye::CALIB_FIX_K4 ? " +fix_k4" : "")
				<< (flag & cv::fisheye::CALIB_RECOMPUTE_EXTRINSIC ? " +recompute_extrinsic" : "");
		}
		else
		{
			flagsStringStream << "flags:"
				<< (flag & cv::CALIB_USE_INTRINSIC_GUESS ? " +use_intrinsic_guess" : "")
				<< (flag & cv::CALIB_FIX_ASPECT_RATIO ? " +fix_aspectRatio" : "")
				<< (flag & cv::CALIB_FIX_PRINCIPAL_POINT ? " +fix_principal_point" : "")
				<< (flag & cv::CALIB_ZERO_TANGENT_DIST ? " +zero_tangent_dist" : "")
				<< (flag & cv::CALIB_FIX_K1 ? " +fix_k1" : "")
				<< (flag & cv::CALIB_FIX_K2 ? " +fix_k2" : "")
				<< (flag & cv::CALIB_FIX_K3 ? " +fix_k3" : "")
				<< (flag & cv::CALIB_FIX_K4 ? " +fix_k4" : "")
				<< (flag & cv::CALIB_FIX_K5 ? " +fix_k5" : "");
		}
		fs.writeComment(flagsStringStream.str());
	}*/

	calibData.flags = flag;

	calibData.fisheye_model = useFisheye;

	calibData.camera_matrix = cameraMatrix;
	calibData.distortion_coefficients = distCoeffs;

	calibData.avg_reprojection_error = totalAvgErr;
	/*if (!reprojErrs.empty())
		fs << "per_view_reprojection_errors" << Mat(reprojErrs);*/

	if (!rvecs.empty() && !tvecs.empty())
	{
		CV_Assert(rvecs[0].type() == tvecs[0].type());
		Mat bigmat((int)rvecs.size(), 6, CV_MAKETYPE(rvecs[0].type(), 1));
		bool needReshapeR = rvecs[0].depth() != 1 ? true : false;
		bool needReshapeT = tvecs[0].depth() != 1 ? true : false;

		for (size_t i = 0; i < rvecs.size(); i++)
		{
			Mat r = bigmat(cv::Range(int(i), int(i + 1)), cv::Range(0, 3));
			Mat t = bigmat(cv::Range(int(i), int(i + 1)), cv::Range(3, 6));

			if (needReshapeR)
				rvecs[i].reshape(1, 1).copyTo(r);
			else
			{
				//*.t() is MatExpr (not Mat) so we can use assignment operator
				CV_Assert(rvecs[i].rows == 3 && rvecs[i].cols == 1);
				r = rvecs[i].t();
			}

			if (needReshapeT)
				tvecs[i].reshape(1, 1).copyTo(t);
			else
			{
				CV_Assert(tvecs[i].rows == 3 && tvecs[i].cols == 1);
				t = tvecs[i].t();
			}
		}
		//fs.writeComment("a set of 6-tuples (rotation vector + translation vector) for each view");
		calibData.extrinsic_parameters = bigmat;
	}

	calibData.valid = true;

	//fs << "}";
}

static bool runCalibrationAndSave(CalibrationData& calibData, Size imageSize, Mat& cameraMatrix, Mat& distCoeffs, vector<vector<Point2f>> imagePoints)
{
	vector<Mat> rvecs, tvecs;
	vector<float> reprojErrs;
	double totalAvgErr = 0;
	vector<Point3f> newObjPoints;

	bool ok = runCalibration(imageSize, cameraMatrix, distCoeffs, imagePoints, rvecs, tvecs, reprojErrs,
		totalAvgErr, newObjPoints);
	cout << (ok ? COL("32") "Calibration succeeded." : COL("31") "Calibration failed.")
		<< COLD " avg re projection error = " << totalAvgErr << endl;

	if (ok)
	    saveCameraParams(calibData, imageSize, cameraMatrix, distCoeffs, rvecs, tvecs, reprojErrs, totalAvgErr);
	return ok;
}