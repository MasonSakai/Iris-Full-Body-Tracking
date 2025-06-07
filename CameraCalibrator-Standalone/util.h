#pragma once
#include <vector>
#include <string>
#include <opencv2/core.hpp>
#include <nlohmann/json.hpp>

using std::wstring;
using std::string;
using std::vector;
using cv::Mat;
using nlohmann::json;

wstring getAppdata();
vector<string> string_split(const string& text, char delimiter);

Mat LoadMat(json& config);
json SaveMat(Mat& mat);
