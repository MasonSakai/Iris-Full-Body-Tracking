#include "App_CalibrateCamera.h"
#include <opencv2/core.hpp>
#include <opencv2/imgcodecs.hpp>
#include <opencv2/highgui.hpp>
#include "ConsoleMacros.h"

using cv::Mat;

vector<Mat> images;

static void PrintCommands() {
	cout << CSI "4;0f" CSI "0J";
	cout << CUL("e") "xit, " CUL("r") "eview images, press space to take image" << endl;
	cout << "(Commands are recieved via the created window)" CSP;
	cout << endl << endl << "Number of images: " << images.size() << CRP;
}

void App_CalibrateCamera(int cameraIndex, CameraData* cameraData) {

	cout << CSI "4;0f" CSI "0J";

	int c;


	cv::VideoCapture cap;

	cap.open(cameraIndex, cv::CAP_ANY);

	if (!cap.isOpened()) {
		cout << "ERROR! Unable to open camera\n";
		return;
	}

	{
		Mat frame;
		cap.read(frame);
		cv::imshow("Image Review", frame);
	}

	PrintCommands();

input:
	while ((c = cv::pollKey()) < 0) {
		Mat frame;
		cap.read(frame);
		cv::imshow("Image Review", frame);
	}
	switch (c)
	{
	case ' ': {
		Mat frame;
		cap.read(frame);
		cv::imshow("Image Review", frame);
		images.push_back(frame);

		PrintCommands();
		break;
	}
	case 'i': {

		cout << CSI "4;0f" CSI "0J";
		cout << "press d to discard, escape to cancel, and anything else to continue" << endl;
		cout << "(Commands are recieved via the created window)" CSP;

		vector<int> toRemove;
		for (int i = 0; i < images.size(); i++) {
			cout << endl << endl << "Index: " << i << CRP;
			cv::imshow("Image Review", images[i]);
			c = cv::waitKey();
			if (c == 27) break;
			else if (c == 'd') toRemove.push_back(i);
		}
		for (int i = toRemove.size() - 1; i >= 0; i--) {
			images.erase(images.begin() + toRemove[i]);
		}

		PrintCommands();
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
	images.clear();
	cv::destroyWindow("Image Review");
	return;
}