#include "CameraData.h"
#include <iostream>
#include "util.h"
#include <fstream>
#include <nlohmann/json.hpp>

using nlohmann::json;

std::map<string, CameraPrefab> prefabs;
std::vector<CameraData> cameras;
static wstring path_;

static CalibrationData LoadCalibrationData(json& config) {
	if (config.is_null()) {
		return CalibrationData();
	}
	else {
		CalibrationData data;
		data.valid = true;

		data.time = config["time"];
		data.nr_max = config["nr_max"];

		data.image_width = config["image_width"];
		data.image_height = config["image_height"];
		data.board_width = config["board_width"];
		data.board_height = config["board_height"];
		data.square_size = config["square_size"];
		data.marker_size = config["marker_size"];

		data.flags = config["flags"];
		data.fisheye_model = config["fisheye_model"];

		data.camera_matrix = LoadMat(config["camera_matrix"]);
		data.dist_coeffs = LoadMat(config["dist_coeffs"]);

		data.avg_reprojection_error = config["avg_reprojection_error"];


		return data;
	}
}
static json SaveCalibrationData(CalibrationData& data) {
	if (!data.valid) {
		return json();
	}
	else {
		json config = json::object();

		config["time"] = data.time;
		config["nr_max"] = data.nr_max;

		config["image_width"] = data.image_width;
		config["image_height"] = data.image_height;
		config["board_width"] = data.board_width;
		config["board_height"] = data.board_height;
		config["square_size"] = data.square_size;
		config["marker_size"] = data.marker_size;

		config["flags"] = data.flags;
		config["fisheye_model"] = data.fisheye_model;

		config["camera_matrix"] = SaveMat(data.camera_matrix);
		config["dist_coeffs"] = SaveMat(data.dist_coeffs);

		config["avg_reprojection_error"] = data.avg_reprojection_error;

		return config;
	}
}

static USBDeviceAddress LoadUSBDeviceAddress(json& config) {
	USBDeviceAddress data;
	data.vendorID = config["vendorID"].get<uint16_t>();
	data.productID = config["productID"].get<uint16_t>();
	data.interfaceNum = config["interfaceNum"].get<uint8_t>();
	data.serialString = config["serialString"].get<string>();
	return data;
}
static json SaveUSBDeviceAddress(USBDeviceAddress& data) {
	json j;
	j["vendorID"] = data.vendorID;
	j["productID"] = data.productID;
	j["interfaceNum"] = data.interfaceNum;
	j["serialString"] = data.serialString;
	return j;
}


bool LoadCameraPrefabs() {

	if (path_.empty()) {
		path_ = getAppdata();
	}

	std::ifstream f(path_ + L"/cameraPrefabs.json");
	if (f.good()) {
		try {
			auto config_ = json::parse(f);
			if (config_.is_null()) {
				config_ = json::object();
			}

			for (auto& pref : config_.items()) {
				json config = pref.value();
				CameraPrefab prefab;
				prefab.prefabName = pref.key();
				prefab.address = LoadUSBDeviceAddress(config["address"]);
				prefab.calibration = LoadCalibrationData(config["calibration"]);
				prefabs[pref.key()] = prefab;
			}

			return true;
		}
		catch (std::exception e) {
			std::cout << "Exception reading camera config: " << e.what() << std::endl;
			return false;
		}
	}

	return false;
}
bool SaveCameraPrefabs() {
	std::ofstream f(path_ + L"/cameraPrefabs.json");
	if (!f.is_open()) return false;

	json config_ = json::object();

	for (auto& prefab : prefabs) {
		json j = json::object();
		CameraPrefab p = prefab.second;
		//j["name"] = p.prefabName;
		j["address"] = SaveUSBDeviceAddress(p.address);
		j["calibration"] = SaveCalibrationData(p.calibration);
		config_[prefab.first] = j;
		std::cout << prefab.first << ": " << j << std::endl;
	}

	f << std::setw(4) << config_;
	f.close();

	return true;
}

bool LoadCameraData() {

	if (path_.empty()) {
		path_ = getAppdata();
	}

	std::ifstream f(path_ + L"/cameraData.json");
	if (f.good()) {
		try {
			auto config_ = json::parse(f);
			if (config_.is_null()) {
				config_ = json::array();
			}

			for (auto& cam : config_) {
				CameraData data;
				data.cameraName = cam["name"];
				data.address = LoadUSBDeviceAddress(cam["address"]);
				data.calibration = LoadCalibrationData(cam["calibration"]);
				if (cam.contains("prefab")) data.prefab = &prefabs[cam["prefab"]];
				cameras.push_back(data);
			}

			return true;
		}
		catch (std::exception e) {
			std::cout << "Exception reading camera config: " << e.what() << std::endl;
			return false;
		}
	}

	return false;
}
bool SaveCameraData() {
	std::ofstream f(path_ + L"/cameraData.json");
	if (!f.is_open()) return false;

	json config_ = json::array();

	for (auto& cam : cameras) {
		json j = json::object();
		j["name"] = cam.cameraName;
		j["address"] = SaveUSBDeviceAddress(cam.address);
		j["calibration"] = SaveCalibrationData(cam.calibration);
		if (cam.prefab != nullptr) j["prefab"] = cam.prefab->prefabName;
		config_.push_back(j);
		//std::cout << j << std::endl;
	}

	f << std::setw(4) << config_;
	f.close();

	return true;
}

bool GetAddressFromDevicePath(string path, USBDeviceAddress& addr) {
	vector<string> split = string_split(path, '#');

	if (split.size() == 1) {
		return false;
	}

	string str = split.at(1);
	addr.serialString = split.at(2);

	split.clear();
	split = string_split(str, '&');

	addr.vendorID = (uint16_t)stoul(split.at(0).substr(4, 4), nullptr, 16);
	addr.productID = (uint16_t)stoul(split.at(1).substr(4, 4), nullptr, 16);

	if (split.size() == 3) addr.interfaceNum = (uint8_t)stoul(split.at(2).substr(3, 2), nullptr, 16);

	return true;
}


CameraData* FindCameraData(USBDeviceAddress& address) {
	for (auto& camera : cameras) {
		if (camera.address == address) {
			return &camera;
		}
	}
	return nullptr;
}
CameraPrefab* FindCameraPrefab(USBDeviceAddress& address, bool checkVendorID, bool checkProductID, bool checkInterfaceNum, bool checkSerialString) {
	for (auto& pair : prefabs) {
		CameraPrefab& prefab = prefabs[pair.first];
		if (   (!checkVendorID || prefab.address.vendorID == address.vendorID)
			&& (!checkProductID || prefab.address.productID == address.productID)
			&& (!checkInterfaceNum || prefab.address.interfaceNum == address.interfaceNum)
			&& (!checkSerialString || prefab.address.serialString == address.serialString)) {
			return &prefab;
		}
	}
	return nullptr;
}


bool RegisterCamera(CameraEnum* cam, USBDeviceAddress& addr) {
	if (FindCameraData(addr) != nullptr) return false;

	CameraData data;
	data.cameraName = cam->description;
	data.address = addr;
	cameras.push_back(data);

	return true;
}
bool RegisterCamera(CameraEnum* cam, USBDeviceAddress& addr, CameraPrefab* prefab) {
	if (FindCameraData(addr) != nullptr) return false;

	CameraData data;
	data.cameraName = cam->description;
	data.address = addr;
	data.prefab = prefab;
	cameras.push_back(data);

	return true;
}