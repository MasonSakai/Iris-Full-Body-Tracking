#pragma once
#include <vector>
#include <string>

using namespace std;

struct CameraEnum {
	string description;
	string devicePath;
};

vector<CameraEnum>* GetCams();
