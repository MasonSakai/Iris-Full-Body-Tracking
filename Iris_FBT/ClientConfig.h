#pragma once
#include <openvr_driver.h>
#include <nlohmann/json.hpp>
#include <string>
using nlohmann::json;
using std::string;
using std::wstring;

namespace IrisFBT {

	class ClientConfig
	{
	public:

		ClientConfig(wstring);

		bool Load();
		bool Save() const;

		json& Get();

	private:

		json config_;

		wstring path_;
	};

	extern ClientConfig Config_SteamVR;

}