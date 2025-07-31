#include "ClientConfig.h"
#include "util.h"
#include <fstream>
#include <iostream>
using std::lock_guard;

using namespace IrisFBT;

mutex ClientConfig::config_mutex_;
json ClientConfig::config_;
wstring ClientConfig::path_;

bool ClientConfig::Load() {
	lock_guard<mutex> lg(config_mutex_);

	if (path_.empty()) {
		path_ = getAppdata() + L"/ClientConfig.json";
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

bool ClientConfig::Save() {
	lock_guard<mutex> lg(config_mutex_);

	std::ofstream f(path_);
	if (!f.is_open()) return false;

	f << std::setw(4) << config_;
	f.close();

	return true;
}

bool ClientConfig::Find(json& config, string ident, bool onlyName) {
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

json& ClientConfig::Get() { lock_guard<mutex> lg(config_mutex_); return config_; }

json& ClientConfig::Get(string name) { lock_guard<mutex> lg(config_mutex_); return config_[name]; }