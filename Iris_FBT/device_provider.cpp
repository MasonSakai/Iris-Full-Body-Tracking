#include "device_provider.h"
#include <iomanip>
#include <sstream>
using namespace IrisFBT;

DeviceProvider* device_provider_ = nullptr;

vr::EVRInitError DeviceProvider::Init(vr::IVRDriverContext* pDriverContext) {
    VR_INIT_SERVER_DRIVER_CONTEXT(pDriverContext);

    vr::VRDriverLog()->Log("Hello world!");

    //TrackedDeviceClass_GenericTracker
    //TrackedDeviceClass_TrackingReference

    my_devices_[IrisTracker_Chest] = std::make_unique<IrisTrackerDevice>(IrisTracker_Chest);


    for (int i = 0; i < IrisTracker_Count; i++) {
        if (my_devices_[i] != nullptr) {
            my_devices_[i]->Register();
        }
    }


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
    mtx_deviceTrackingData.lock();
    for (int i = 0; i < IrisTracker_Count; i++) {
        if (my_devices_[i] != nullptr) {
            my_devices_[i]->RunFrame();
        }
    }
    mtx_deviceTrackingData.unlock();
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

IrisTrackerDevice* DeviceProvider::GetDevice(IrisTrackerIndex index) {
    if (index >= IrisTracker_Count || index < 0) {
        std::stringstream stream;
        stream << "Attempted to get device out of range: 0x" << std::hex << index;
        vr::VRDriverLog()->Log(stream.str().c_str());
        return nullptr;
    }
    return my_devices_[index].get();
}