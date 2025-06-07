#include "ConsoleApplication.h"
#include "App_CalibrateCamera.h"
#include <opencv2/core.hpp>
#include <opencv2/imgcodecs.hpp>
#include <opencv2/highgui.hpp>
#include <opencv2/calib3d.hpp>
#include <iostream>
#include <wtypes.h>
#include "ConsoleMacros.h"
#include <conio.h>

using namespace std;


bool EnableVTMode()
{
	// Set output mode to handle virtual terminal sequences
	HANDLE hOut = GetStdHandle(STD_OUTPUT_HANDLE);
	if (hOut == INVALID_HANDLE_VALUE)
	{
		return false;
	}

	DWORD dwMode = 0;
	if (!GetConsoleMode(hOut, &dwMode))
	{
		return false;
	}

	dwMode |= ENABLE_VIRTUAL_TERMINAL_PROCESSING;
	if (!SetConsoleMode(hOut, dwMode))
	{
		return false;
	}
	return true;
}

vector<CameraEnum>* cams;
int selectedCam = 0;

void PrintCams() {

	CameraEnum* cam;
	USBDeviceAddress addr;
	for (size_t i = 0; i < cams->size(); i++)
	{
		cam = &cams->at(i);
		cout << (selectedCam == i ? ">" : " ") << "Camera " << i << ":\t" << cam->description << endl;
		if (GetAddressFromDevicePath(cam->devicePath, addr)) {
			CameraData* data = FindCameraData(addr);
			if (data == nullptr) {
				cout << COL("31") << "\tUnregistered Camera" << COLD << endl;
			}
			else {
				cout << COL("32") << "\tRegistered as " << data->cameraName << COLD << endl;
			}
		}
		else {
			cout << COL("31") << "\tUnknown Path: " << cam->devicePath << COLD << endl;
		}
	}
}

static void PrintCommands() {
	cout << CSI "4;0f" CSI "0J";
	cout << CUL("e") "xit, " CUL("s") "elect camera, "  CUL("v") "iew camera, "  CUL("r") "egister camera, "  CUL("m") "anage camera, " CUL("c") "alibrate camera, apply "  CUL("p") "refab, recheck " CUL("h") "ardware" << endl;
	cout << "Give command: " CSP;
}

void StartConsoleApplication()
{
	cams = GetCams();

	char c;
	int i;
	PrintCommands();
	cout << endl << endl;
	PrintCams();
	cout << CRP;
	
input:
	c = _getch();
	cout << CRCD << c << endl << endl;
	switch (c)
	{
	case 's': {
		PrintCams();
		cout << endl << "select camera (0-" << cams->size() - 1 << "): " CSP;
		while (true) {
			cin >> i;
			if (i < 0 || i >= cams->size()) {
				cout << "\x07" CRCD;
				continue;
			}
			selectedCam = i;
			PrintCommands();
			cout << endl << endl;
			PrintCams();
			cout << CRP;
			break;
		}
		break;
	}
	case 'v': {
		cv::VideoCapture cap;
		cap.open(selectedCam, cv::CAP_ANY);

		/*cap.set(cv::CAP_PROP_FRAME_WIDTH, 1280);
		cap.set(cv::CAP_PROP_FRAME_HEIGHT, 720);*/

		cv::Mat frame, frameCopy;
		cap.read(frame);
		cv::imshow("Image Review", frame);
		cout << endl << endl << "Press any key on the window to continue " << frame.size();
		bool undistort = false;
		CalibrationData* calib = nullptr;
		Mat scaled_camera_matrix;
		{
			USBDeviceAddress addr;
			if (GetAddressFromDevicePath(cams->at(selectedCam).devicePath, addr)) {
				auto cam = FindCameraData(addr);
				calib = cam->calibration.valid ? &cam->calibration
					  : cam->prefab != nullptr ? &cam->prefab->calibration
					  : nullptr;
				if (calib != nullptr) {
					scaled_camera_matrix = cv::getOptimalNewCameraMatrix(
						calib->camera_matrix, calib->dist_coeffs,
						{ calib->image_width, calib->image_height },
						1, frame.size()
					);
				}
			}
		}
		while (true) {
			cap.read(frame);
			if (undistort) {
				frame.copyTo(frameCopy);
				cv::undistort(frameCopy, frame, scaled_camera_matrix, calib->dist_coeffs);
			}
			cv::imshow("Image Review", frame);
			c = cv::pollKey();
			if (c == 'd') {
				undistort ^= calib != nullptr;
			}
			else if (c >= 0) break;
		}
		cv::destroyWindow("Image Review");
		cap.release();

		PrintCommands();
		cout << endl << endl;
		PrintCams();
		cout << CRP;
		break;
	}
	case 'r': {
		CameraEnum* cam = &cams->at(selectedCam);
		USBDeviceAddress addr;
		if (GetAddressFromDevicePath(cam->devicePath, addr)) {
			CameraData* exdata = FindCameraData(addr);
			if (exdata != 0) {
				PrintCommands();
				cout << endl << endl;
				cout << COL("31") "Camera already exits" COLD " (" << exdata->cameraName << ")" CRP;
				break;
			}
			CameraPrefab* prefab = FindCameraPrefab(addr);
			if (prefab == 0) {
				RegisterCamera(cam, addr);
			}
			else {
				cout << "Found Prefab matching camera: " << prefab->prefabName << endl;
				cout << "Apply prefab (y/n/c): ";
				cin >> c;
				switch (c)
				{
				case 'y':
				case 'Y':
					RegisterCamera(cam, addr, prefab);
					break;
				case 'n':
				case 'N':
					RegisterCamera(cam, addr);
					break;
				case 'c':
				default:
					cout << CRCD;
					goto input;
				}
			}
			PrintCommands();
			cout << endl << endl;
			PrintCams();
			cout << endl << endl;
			cout << "Camera Registered: " << cam->description;
			SaveCameraData();
			cout << CRP;
		}
		else {
			PrintCommands();
			cout << endl << endl;
			cout << "Error with cam " << cam->devicePath;
			cout << CRP;
		}
		break;
	}
	case 'c': {
		USBDeviceAddress addr;
		if (GetAddressFromDevicePath(cams->at(selectedCam).devicePath, addr)) {
			CameraData* data = FindCameraData(addr);
			if (data == nullptr) {
				PrintCommands();
				cout << endl << endl;
				PrintCams();
				cout << endl << endl;
				cout << COL("31") "Camera is not registered" COLD CRP;
				break;
			}
			App_CalibrateCamera(selectedCam, data->calibration);
			PrintCommands();
			cout << endl << endl;
			PrintCams();
			cout << endl << endl;
			SaveCameraPrefabs();
			SaveCameraData();
			cout << "Exited Calibration" CRP;
		}
		else {
			PrintCommands();
			cout << endl << endl;
			PrintCams();
			cout << endl << endl;
			cout << "Failed Calibration" CRP;
		}
		break;
	}
	case 'h': {
		cams = GetCams();
		selectedCam = 0;
		PrintCommands();
		cout << endl << endl;
		PrintCams();
		cout << CRP;
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
	return;
}