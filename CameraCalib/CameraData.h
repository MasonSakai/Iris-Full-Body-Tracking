#pragma once

#include <vector>
#include <string>
#include "CameraEnum.h"
#include <opencv2/core/persistence.hpp>


using namespace std;


struct CalibrationData {
	bool valid = false;
};

cv::FileStorage& operator<<(cv::FileStorage& fs, CalibrationData& cd);
void operator>>(const cv::FileNode& node, CalibrationData& cd);

struct USBDeviceAddress {
	uint16_t VendorID = 0;
	uint16_t ProductID = 0;
	uint8_t interfaceNum = 0;
	string serialString = "";
};

struct CameraPrefab {
	string prefabName;
	USBDeviceAddress address;
	CalibrationData calibration;
};
struct CameraData {
	string cameraName;
	string prefabName;
	USBDeviceAddress address;
	CalibrationData calibration;
};

//move elsewhere?
void StringSplit(string str, string delimiter, vector<string>* buffer);

/// <summary>
/// Loads the camera data from file<para />
/// ONLY RUN ONCE
/// </summary>
/// <param name="path">The file path to the camera data</param>
/// <returns>Whether the file was found and read successfully</returns>
bool LoadCameraData(string path);
bool SaveCameraData(string path);


USBDeviceAddress GetAddressFromDevicePath(string path);
CameraData* FindCameraData(USBDeviceAddress &address);

CameraPrefab* FindCameraPrefab(USBDeviceAddress& address);

void RegisterCamera(CameraData data);
void RegisterCamera(CameraEnum* data, string prefabName = "");
void RegisterCamera(CameraEnum* data, CameraPrefab* prefab);
void RegisterCamera(CameraEnum* data, USBDeviceAddress addr, string prefabName = "");
void RegisterCamera(CameraEnum* data, USBDeviceAddress addr, CameraPrefab* prefab);