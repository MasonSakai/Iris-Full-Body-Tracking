#pragma once
#include <vector>
#include <string>
#include <nlohmann/json.hpp>
using nlohmann::json;
using std::string;
using std::wstring;
using std::vector;

namespace IrisFBT {

	wstring getAppdata();
	wstring getDriverPath();

	vector<string> split(const string& text, char delimiter);

}
