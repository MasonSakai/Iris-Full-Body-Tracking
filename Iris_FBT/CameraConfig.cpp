#include "CameraConfig.h"
#include "util.h"
#include <fstream>
#include <iostream>
using std::lock_guard;

using namespace IrisFBT;

mutex CameraConfig::config_mutex_;
json CameraConfig::config_;
wstring CameraConfig::path_;

bool CameraConfig::Load() {
	lock_guard<mutex> lg(config_mutex_);

	if (path_.empty()) {
		path_ = getAppdata() + L"/cameraConfig.json";
	}

	std::ifstream f(path_);
	if (!f.good()) {
		config_ = json::object();
		return false;
	}

	try {
		config_ = json::parse(f);
		if (config_.is_null()) {
			config_ = json::object();
		}
		return true;
	}
	catch (std::exception e) {
		std::cout << "Exception reading camera config: " << e.what() << std::endl;
		config_ = json::object();
		return false;
	}
}

bool CameraConfig::Save() {
	lock_guard<mutex> lg(config_mutex_);

	std::ofstream f(path_);
	if (!f.is_open()) return false;

	f << std::setw(4) << config_;
	f.close();

	return true;
}

bool CameraConfig::Rename(string old_name, string new_name) {
	return change_key(config_, old_name, new_name);
}

bool CameraConfig::Find(json& config, string ident, bool onlyName) {
	lock_guard<mutex> lg(config_mutex_);

	if (config_.contains(ident)) {
		config = config_[ident];
		return true;
	}

	if (!onlyName) {

		for (auto& camera : config_) {
			if (camera.contains("camera_name") && camera["camera_name"].get<string>() == ident) {
				config = camera;
				return true;
			}
		}
	}

	return false;
}

json& CameraConfig::Get() { lock_guard<mutex> lg(config_mutex_); return config_; }

json& CameraConfig::Get(string name) { lock_guard<mutex> lg(config_mutex_); return config_[name]; }