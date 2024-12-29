// CameraCalib.cpp : This file contains the 'main' function. Program execution begins and ends there.
//
#include <opencv2/videoio.hpp>
#include "CameraEnum.h"
#include "CameraData.h"
#include <iostream>

using namespace std;
using namespace cv;

int main(int argc, char* argv[])
{
	string cdpath = string(argv[1]) + "\\CameraData.json";
	LoadCameraData(cdpath);

    vector<CameraEnum>* cams = GetCams();

	CameraEnum* cam;
	for (size_t i = 0; i < cams->size(); i++)
	{
		cam = &cams->at(i);
		cout << "Camera " << i << ":\t" << cam->description << "\t(" << cam->devicePath << ")" << endl;
		USBDeviceAddress addr = GetAddressFromDevicePath(cam->devicePath);
		cout << '\t' << addr.VendorID << "\t" << addr.ProductID << "\t" << addr.serialString << endl;
		CameraData* data = FindCameraData(addr);
		cout << '\t' << data << endl;
		if (data == 0) {
			CameraData newData;
			newData.address = addr;
			newData.cameraName = cam->description;
			RegisterCamera(newData);
		}
	}

	SaveCameraData(cdpath);

	//VideoCapture cap;
}

/*
* https://community.silabs.com/s/article/windows-usb-device-path?language=en_US
Camera 0:       Global Shutter Camera   (\\?\usb#vid_32e4&pid_0234&mi_00#6&325db0ba&0&0000#{65e8773d-8f56-11d0-a3b9-00a0c9223196}\global)
Camera 1:       USB2.0 HD UVC WebCam    (\\?\usb#vid_13d3&pid_5666&mi_00#6&2f2fc667&0&0000#{65e8773d-8f56-11d0-a3b9-00a0c9223196}\global)
Camera 2:       Global Shutter Camera   (\\?\usb#vid_32e4&pid_0234&mi_00#6&ec95057&0&0000#{65e8773d-8f56-11d0-a3b9-00a0c9223196}\global)
*/