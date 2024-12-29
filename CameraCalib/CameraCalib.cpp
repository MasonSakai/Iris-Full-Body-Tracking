// CameraCalib.cpp : This file contains the 'main' function. Program execution begins and ends there.
//
#include <opencv2/videoio.hpp>
#include "CameraEnum.h"
#include "CameraData.h"
#include <iostream>

using namespace std;
using namespace cv;

vector<CameraEnum>* cams;

int selectedCam = 0;

int main(int argc, char* argv[])
{

	string cdpath = string(argv[1]) + "\\CameraData.json";
	LoadCameraData(cdpath);

    cams = GetCams();

	CameraEnum* cam;
	for (size_t i = 0; i < cams->size(); i++)
	{
		cam = &cams->at(i);
		cout << "Camera " << i << ":\t" << cam->description << "\t(" << cam->devicePath << ")" << endl;
		USBDeviceAddress addr = GetAddressFromDevicePath(cam->devicePath);
		CameraData* data = FindCameraData(addr);
		if (data == 0) {
			cout << "\t\033[31mUnregistered Camera\033[0m" << endl;
		}
	}

	char c;
	int i;
	VideoCapture cap;
	while (true) {
		cout << endl << "s to select camera, e to exit" << endl;
		cout << "Give command: \x1B[s";
	input:
		cin >> c;
		cout << "\x1B[u\x1B[0J" << c << endl;
		switch (c)
		{
		case 's':
			cout << "select camera (0-" << cams->size() - 1 << "; -1 to cancel): \x1B[s";
			while (true) {
				cin >> i;
				if (i == -1) {
					cout << "\x1B[u\x1b[3F\x1B[0J";
					break;
				}
				if (i < 0 || i >= cams->size()) {
					cout << "\x07\x1B[u\x1B[0J";
					continue;
				}
				selectedCam = i;
				cout << "\x1B[u\r\x1B[0J" << "Selected camera: " << i << endl;
				break;
			}
			break;
		case 'e':
			goto exit;
		default:
			cout << "\x07\x1B[u\x1B[0J";
			goto input;
		}
	}
exit:

	SaveCameraData(cdpath);
}

/*
* https://community.silabs.com/s/article/windows-usb-device-path?language=en_US
* https://gist.github.com/fnky/458719343aabd01cfb17a3a4f7296797
Camera 0:       Global Shutter Camera   (\\?\usb#vid_32e4&pid_0234&mi_00#6&325db0ba&0&0000#{65e8773d-8f56-11d0-a3b9-00a0c9223196}\global)
Camera 1:       USB2.0 HD UVC WebCam    (\\?\usb#vid_13d3&pid_5666&mi_00#6&2f2fc667&0&0000#{65e8773d-8f56-11d0-a3b9-00a0c9223196}\global)
Camera 2:       Global Shutter Camera   (\\?\usb#vid_32e4&pid_0234&mi_00#6&ec95057&0&0000#{65e8773d-8f56-11d0-a3b9-00a0c9223196}\global)
*/