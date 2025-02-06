#pragma once
#include <opencv2/core.hpp>

void GetModel(bool is_cuda = true);

void RunModel(cv::Mat image);