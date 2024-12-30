
#include "CameraCalibration.h"
#include <iostream>
#include <opencv2/core.hpp>
#include <opencv2/imgcodecs.hpp>
#include <opencv2/highgui.hpp>
#include <opencv2/aruco/charuco.hpp>
#include <opencv2/objdetect/aruco_dictionary.hpp>
#include "ConsoleMacros.h"

using namespace std;
using namespace cv;

aruco::CharucoBoard* board;


CalibrationData PerformCalibration(Mat* images[], int nImages) {
	if(board == nullptr) GenerateCalibrationBoard();

	
	cout << "imdisplay" << endl;
	for (int i = 0; i < nImages; i++) {
		imshow("display", *images[i]);
		waitKey();
	}
	destroyWindow("display");
	CalibrationData data;
	return data;
}


void App_CalibrateCamera(int camIndex, CameraData* camData) {

	vector<Mat*> capturedFrames;

	VideoCapture cap;

	cap.open(camIndex, CAP_ANY);

	if (!cap.isOpened()) {
		cerr << "ERROR! Unable to open camera\n";
		return;
	}

	cout << "Backend: " << cap.get(CAP_PROP_BACKEND) << ", " << cap.getBackendName() << endl;
	cout << "FPS: " << cap.get(CAP_PROP_FPS) << endl;
	cout << "Please capture at least 10 frames with the calibration sheet" << endl;
	cout << "The more varied the positions and angles the better, so long as the whole sheet is visible" << endl;
	cout << CSP;

	Mat frame;
	//--- GRAB AND WRITE LOOP
	int key;
resetConsole:
	cout << CRCD;
	cout << "Press c to capture frame" << endl
		 << "Press p to process frames" << endl
		 << "Press e to terminate" << endl;
	for (;;)
	{
		// wait for a new frame from camera and store it into 'frame'
		cap.read(frame);
		// check if we succeeded
		if (frame.empty()) {
			cerr << "ERROR! blank frame grabbed\n";
			break;
		}
		// show live and wait for a key with timeout long enough to show images
		imshow("Calibration", frame);
		key = pollKey();
		if (key >= 0) {
			switch ((char)key)
			{
			case 'c': {
				cout << CRCD;
				cout << "Press c to add frame" << endl
					<< "Press e to discard frame" << endl;
				key = waitKey();
				switch ((char)key)
				{
				case 'c': {
					Mat* m = new Mat();
					frame.copyTo(*m);
					capturedFrames.push_back(m);
					break;
				}
				case 'e':
				default:
					break;
				}
				goto resetConsole;
			}
			case 'p': {
				CalibrationData data = PerformCalibration(capturedFrames.data(), capturedFrames.size());
			}
			case 'e':
				goto exit;
			default:
				cout << (char)(key) << endl;
				break;
			}
		}
	}
exit:
	destroyWindow("Calibration");
	for (auto p : capturedFrames)
		delete p;
}

void GenerateCalibrationBoard(int squaresX, int squaresY, float squareLength, float markerLength, int dictionaryId) {

	aruco::Dictionary dictionary = aruco::getPredefinedDictionary(dictionaryId);
	board = new aruco::CharucoBoard(Size(squaresX, squaresY), (float)squareLength, (float)markerLength, dictionary);
}
void DrawCalibrationBoardImage(string path, int squaresX, int squaresY, int squareLength, int borderBits, bool showImage) {

	Size imageSize;
	imageSize.width = squaresX * squareLength;
	imageSize.height = squaresY * squareLength;

	// show created board
	Mat boardImage;
	board->generateImage(imageSize, boardImage, 0, borderBits);

	if (showImage) {
		imshow("board", boardImage);
		waitKey(0);
	}
	destroyWindow("board");

	imwrite(path, boardImage);
}