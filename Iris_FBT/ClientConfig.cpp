#include "ClientConfig.h"
#include "util.h"
#include <fstream>
#include <iostream>

using namespace IrisFBT;

ClientConfig IrisFBT::Config_SteamVR(L"/SteamVR.json");

IrisFBT::ClientConfig::ClientConfig(wstring path)
{
	path_ = getAppdata() + path;
}

bool ClientConfig::Load() {

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

bool ClientConfig::Save() const {

	std::ofstream f(path_);
	if (!f.is_open()) return false;

	f << std::setw(4) << config_;
	f.close();

	return true;
}

json& ClientConfig::Get() { return config_; }