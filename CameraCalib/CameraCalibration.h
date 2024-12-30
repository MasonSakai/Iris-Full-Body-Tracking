#pragma once

#include "CameraData.h"

CalibrationData PerformCalibration(cv::Mat* images[], int nImages);
void App_CalibrateCamera(int camIndex, CameraData* camData);

void GenerateCalibrationBoard(int squaresX = 5, int squaresY = 7, float squareLength = 0.030f, float markerLength = 0.015f, int dictionaryId = 10);
void DrawCalibrationBoardImage(string path, int squaresX = 5, int squaresY = 7, int squareLength = 30, int borderBits = 1, bool showImage = true);