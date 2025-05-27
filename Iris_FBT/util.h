#pragma once
#include <vector>
#include <string>
using std::string;
using std::wstring;
using std::vector;

namespace IrisFBT {

	wstring getAppdata();
	wstring getDriverPath();

	vector<string> split(const string& text, char delimiter);

	string base64_encode(unsigned char const* buf, unsigned int bufLen);
	vector<unsigned char> base64_decode(const string& encoded_string);
}
