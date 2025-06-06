#pragma once

#include "CameraEnum.h"
#include "CameraData.h"

extern vector<CameraEnum>* cams;
extern int selectedCam;

bool EnableVTMode();

void PrintCams();

void StartConsoleApplication();