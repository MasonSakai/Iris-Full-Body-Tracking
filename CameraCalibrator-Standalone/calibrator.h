#pragma once
#include <vector>
#include <opencv2/core.hpp>
#include "CameraData.h"

using std::vector;
using cv::Mat;

bool CalibrateCamera(const CalibrationData* calibData, Mat& image);
void GenerateCalibrator();
void GeneratePattern();