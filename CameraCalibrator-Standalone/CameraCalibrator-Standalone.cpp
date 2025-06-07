#include "CameraData.h"
#include "ConsoleApplication.h"
#include <iostream>

int main()
{
    if (!EnableVTMode()) {
        std::cout << "Failed to setup console!" << std::endl;
        return 1;
    }

    LoadCameraPrefabs();
    LoadCameraPrefabs();

    StartConsoleApplication();

    SaveCameraPrefabs();
    SaveCameraData();
}