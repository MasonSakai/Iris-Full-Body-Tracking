#include "device_provider.h"

vr::EVRInitError DeviceProvider::Init(vr::IVRDriverContext* pDriverContext) {
    VR_INIT_SERVER_DRIVER_CONTEXT(pDriverContext);

    vr::VRDriverLog()->Log("Hello world!");

    my_devices_[IrisTracker_Chest] = std::make_unique<IrisTrackerDevice>(vr::TrackedControllerRole_OptOut);
    vr::VRServerDriverHost()->TrackedDeviceAdded(iris_tracker_serial,
        vr::TrackedDeviceClass_Controller,
        my_devices_[IrisTracker_Chest].get());

    return vr::VRInitError_None;
}

void DeviceProvider::Cleanup() {
    vr::VRDriverLog()->Log("Goodbye world!");

    VR_CLEANUP_SERVER_DRIVER_CONTEXT();
}

const char* const* DeviceProvider::GetInterfaceVersions() {
    return vr::k_InterfaceVersions;
}

void DeviceProvider::RunFrame() {
    for (int i = 0; i < IrisTracker_Count; i++) {
        if (my_devices_[i] != nullptr) {
            my_devices_[i]->RunFrame();
        }
    }
}

bool DeviceProvider::ShouldBlockStandbyMode() {
    return false;
}

void DeviceProvider::EnterStandby() {
    vr::VRDriverLog()->Log("DeviceProvider::EnterStandby");
}

void DeviceProvider::LeaveStandby() {
    vr::VRDriverLog()->Log("DeviceProvider::LeaveStandby");
}