#pragma once
#include <opencv2/core.hpp>

void GetModel(bool isGPU = true);

void RunModel(cv::Mat image);