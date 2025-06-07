#pragma once
#include <vector>
#include <string>
#include <map>
#include "CameraEnum.h"
#include <opencv2/core.hpp>

using std::string;
using std::map;
using std::vector;
using cv::Mat;

struct CalibrationData {
	bool valid = false;

	string time;
	int nr_max;

	int image_width, image_height;
	int board_width, board_height;
	float square_size, marker_size;
	uint32_t flags;
	bool fisheye_model;
	Mat camera_matrix, dist_coeffs;
	double avg_reprojection_error;
	Mat extrinsic_parameters;
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
	string prefabName = "";
	USBDeviceAddress address;
	CalibrationData calibration;
};
struct CameraData {
	string cameraName = "";
	CameraPrefab* prefab = nullptr;
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