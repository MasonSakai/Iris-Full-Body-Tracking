// CameraCalib.cpp : This file contains the 'main' function. Program execution begins and ends there.
//
#include "ConsoleApplication.h"
#include <iostream>
#include <opencv2/core/utils/logger.hpp>
#include "CameraCalibration.h"

using namespace std;


int main(int argc, char* argv[])
{
	cv::utils::logging::setLogLevel(cv::utils::logging::LogLevel::LOG_LEVEL_SILENT);

	bool fSuccess = EnableVTMode();
	if (!fSuccess)
	{
		cout << "Unable to enter VT processing mode. Quitting." << endl;
		return -1;
	}

	string basePath = string(argc > 1 ? argv[1] : "C:\\Users\\User\\source\\repos\\Iris-Full-Body-Tracking\\_persistance");

	string cdpath = basePath + "\\CameraData.json";
	LoadCameraData(cdpath);

	StartConsoleApplication();

	SaveCameraData(cdpath);
}

/*
* https://community.silabs.com/s/article/windows-usb-device-path?language=en_US
* https://gist.github.com/fnky/458719343aabd01cfb17a3a4f7296797
Camera 0:       Global Shutter Camera   (\\?\usb#vid_32e4&pid_0234&mi_00#6&325db0ba&0&0000#{65e8773d-8f56-11d0-a3b9-00a0c9223196}\global)
Camera 1:       USB2.0 HD UVC WebCam    (\\?\usb#vid_13d3&pid_5666&mi_00#6&2f2fc667&0&0000#{65e8773d-8f56-11d0-a3b9-00a0c9223196}\global)
Camera 2:       Global Shutter Camera   (\\?\usb#vid_32e4&pid_0234&mi_00#6&ec95057&0&0000#{65e8773d-8f56-11d0-a3b9-00a0c9223196}\global)
*/