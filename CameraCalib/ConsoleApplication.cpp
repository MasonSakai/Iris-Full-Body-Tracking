
#include "ConsoleApplication.h"
#include "CameraCalibration.h"
#include <iostream>
#include <wtypes.h>
#include "ConsoleMacros.h"

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

static void PrintCams() {

	CameraEnum* cam;
	for (size_t i = 0; i < cams->size(); i++)
	{
		cam = &cams->at(i);
		cout << (selectedCam == i ? ">" : " ") << "Camera " << i << ":\t" << cam->description << endl;
		USBDeviceAddress addr = GetAddressFromDevicePath(cam->devicePath);
		CameraData* data = FindCameraData(addr);
		if (data == 0) {
			cout << COL("31") << "\tUnregistered Camera" << COLD << endl;
		}
		else {
			cout << COL("32") << "\tRegistered as " << data->cameraName << COLD << endl;
		}
	}
}

static void PrintCommands() {
	cout << CSI "4;0f" CSI "0J";
	cout << CUL("e") "xit, " CUL("s") "elect camera, " CUL("r") "egister camera, " CUL("c") "alibrate camera, recheck " CUL("h") "ardware" << endl;
	cout << "Give command: " CSP;
}

void StartConsoleApplication()
{
	cams = GetCams();

	char c;
	int i;
	PrintCommands();
input:
	cin >> c;
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
	case 'r': {
		CameraEnum* cam = &cams->at(selectedCam);
		USBDeviceAddress addr = GetAddressFromDevicePath(cam->devicePath);
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
		cout << "Camera Registered: " << cam->description;
		cout << CRP;
		break;
	}
	case 'c': {
		USBDeviceAddress addr = GetAddressFromDevicePath(cams->at(selectedCam).devicePath);
		CameraData* data = FindCameraData(addr);
		if (data == nullptr) {
			PrintCommands();
			cout << endl << endl;
			cout << COL("31") "Camera is not registered" COLD CRP;
			break;
		}
		App_CalibrateCamera(selectedCam, data);
		PrintCommands();
		cout << endl << endl;
		cout << "Exited Calibration" CRP;
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