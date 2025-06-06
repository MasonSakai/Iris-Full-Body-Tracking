#pragma once
#include <vector>
#include <string>

using std::string;
using std::vector;

struct CameraEnum {
	string description;
	string devicePath;
};

vector<CameraEnum>* GetCams();
