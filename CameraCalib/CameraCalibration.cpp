
#include "CameraCalibration.h"
#include <iostream>
#include <opencv2/core.hpp>
#include <opencv2/imgcodecs.hpp>
#include <opencv2/highgui.hpp>
#include "ConsoleMacros.h"

using namespace std;
using namespace cv;

void CalibrateCamera(int camIndex, CameraData* camData) {

	VideoCapture cap;

	cap.open(camIndex, CAP_ANY);

	if (!cap.isOpened()) {
		cerr << "ERROR! Unable to open camera\n";
		return;
	}

	cout << "Backend: " << cap.get(CAP_PROP_BACKEND) << ", " << cap.getBackendName() << endl;
	cout << "FPS: " << cap.get(CAP_PROP_FPS) << endl;

	Mat frame;
	//--- GRAB AND WRITE LOOP
	cout << CSP;
resetConsole:
	cout << CRP;
	cout << "Press c to capture frame" << endl
		 << "Press e to terminate" << endl;
	int key;
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
}