#pragma once
#include <vector>
#include <string>
#include <nlohmann/json.hpp>
#include <opencv2/core.hpp>
using nlohmann::json;
using std::string;
using std::wstring;
using std::vector;
using cv::Mat;

namespace IrisFBT {

	wstring getAppdata();
	wstring getDriverPath();

	bool change_key(json& object, const std::string& old_key, const std::string& new_key);

	vector<string> split(const string& text, char delimiter);

	string base64_encode(unsigned char const* buf, unsigned int bufLen);
	vector<unsigned char> base64_decode(const string& encoded_string);


}
