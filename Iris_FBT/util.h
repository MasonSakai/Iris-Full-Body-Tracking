#pragma once
#include <vector>
#include <string>
#include <nlohmann/json.hpp>
#include <sio_client.h>
using nlohmann::json;
using std::string;
using std::wstring;
using std::vector;

namespace IrisFBT {

	wstring getAppdata();
	wstring getDriverPath();

	vector<string> split(const string& text, char delimiter);

	json messageToJson(sio::message::ptr);

}
