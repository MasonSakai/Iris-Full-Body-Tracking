#include "Calibrator.h"
#include <opencv2/aruco.hpp>
#include <opencv2/objdetect/charuco_detector.hpp>
#include <opencv2/calib3d.hpp>
#include <opencv2/highgui.hpp>
#include "ConsoleMacros.h"
#include "util.h"

using cv::Point2f;
using cv::Point3f;
using cv::Size;

int charucoDictionaryID = cv::aruco::DICT_4X4_50;
float charucoSquareLength = 0.035142857142857f;
float charucoMarkerLength = 0.018f;

int charucoBoardWidth = 5;
int charucoBoardHeight = 7;

bool useFisheye = false;
int flag = 0;


cv::aruco::Dictionary dictionary;
cv::aruco::CharucoBoard board;
cv::aruco::CharucoDetector detector;


bool runCalibrationAndSave(const CalibrationData* calibData, Size imageSize, Mat& cameraMatrix, Mat& distCoeffs, vector<vector<Point2f>> imagePoints);

bool CalibrateCamera(const CalibrationData* calibData, Mat& image) {

	cout << endl << endl;

	Mat cameraMatrix = Mat::eye(3, 3, CV_64F);
	Mat distCoeffs = Mat::zeros(8, 1, CV_64F);
	float grid_width;

	vector<Point2f> pointBuf;
	vector<int> markerIds;
	detector.detectBoard(image, pointBuf, markerIds);

	bool found = pointBuf.size() == (size_t)((charucoBoardHeight - 1) * (charucoBoardWidth - 1));

	cv::drawChessboardCorners(image, cv::Size(charucoBoardWidth - 1, charucoBoardHeight - 1), Mat(pointBuf), found);
	cv::imshow("Image Review", image);

	cout << "Found? " << found << endl;
    if (!found) return false;
    else {
        runCalibrationAndSave(calibData, image);
    }

	return true;
}