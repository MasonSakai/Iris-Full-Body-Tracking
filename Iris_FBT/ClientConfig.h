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

		static bool Load();
		static bool Save();

		static json& Get();

	private:

		static json config_;

		static wstring path_;
	};

}