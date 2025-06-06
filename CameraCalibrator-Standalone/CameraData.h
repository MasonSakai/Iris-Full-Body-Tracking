#pragma once
#include <vector>
#include <string>
#include <map>
#include "CameraEnum.h"

using std::string;
using std::map;
using std::vector;

struct CalibrationData {
	bool valid = false;
};

struct USBDeviceAddress {
	uint16_t vendorID = 0;
	uint16_t productID = 0;
	uint8_t interfaceNum = 0;
	string serialString = "";

	bool operator==(const USBDeviceAddress& other) const {
		return vendorID == other.vendorID
			&& productID == other.productID
			&& interfaceNum == other.interfaceNum
			&& serialString == other.serialString;
	}
};

struct CameraPrefab {
	string prefabName;
	USBDeviceAddress address;
	CalibrationData calibration;
};
struct CameraData {
	string cameraName;
	CameraPrefab* prefab;
	USBDeviceAddress address;
	CalibrationData calibration;
};

extern map<string, CameraPrefab> prefabs;
extern vector<CameraData> cameras;

bool LoadCameraPrefabs();
bool SaveCameraPrefabs();
bool LoadCameraData();
bool SaveCameraData();

bool GetAddressFromDevicePath(string path, USBDeviceAddress& addr);

CameraData* FindCameraData(USBDeviceAddress& address);
CameraPrefab* FindCameraPrefab(USBDeviceAddress& address, bool checkVendorID = true, bool checkProductID = true, bool checkInterfaceNum = false, bool checkSerialString = false);

bool RegisterCamera(CameraEnum* cam, USBDeviceAddress& addr);
bool RegisterCamera(CameraEnum* cam, USBDeviceAddress& addr, CameraPrefab* prefab);