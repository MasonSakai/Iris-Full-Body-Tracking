#pragma once
#include <openvr_driver.h>
#include <nlohmann/json.hpp>
#include <string>
#include <mutex>
using nlohmann::json;
using std::string;
using std::wstring;
using std::mutex;

namespace IrisFBT {

	class CameraConfig
	{
	public:

		static bool Load();
		static bool Save();

		static bool Rename(string old_name, string new_name);

		static bool Find(json& config, string ident, bool onlyName = false);

		static json& Get();
		static json& Get(string name);

	private:

		static mutex config_mutex_;
		static json config_;

		static wstring path_;
	};

}