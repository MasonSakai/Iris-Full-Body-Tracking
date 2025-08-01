#include "device_provider.h"
#include "ClientConfig.h"
#include <iomanip>
#include <sstream>
#include "IrisSocketClient.h"
using namespace IrisFBT;

namespace IrisFBT {
    DeviceProvider* device_provider = nullptr;
}

vr::EVRInitError DeviceProvider::Init(vr::IVRDriverContext* pDriverContext) {
    VR_INIT_SERVER_DRIVER_CONTEXT(pDriverContext);

    vr::VRDriverLog()->Log("Hello world!");

    device_provider = this;
    ClientConfig::Load();
    iris_client = std::make_unique<IrisSocketClient>(this);

    //TrackedDeviceClass_GenericTracker
    //TrackedDeviceClass_TrackingReference

    return vr::VRInitError_None;
}

void DeviceProvider::Cleanup() {
    vr::VRDriverLog()->Log("Goodbye world!");
    if (iris_client != nullptr)
        iris_client.reset();
    ClientConfig::Save();
    VR_CLEANUP_SERVER_DRIVER_CONTEXT();
}

const char* const* DeviceProvider::GetInterfaceVersions() {
    return vr::k_InterfaceVersions;
}

void DeviceProvider::RunFrame() {
    mtx_deviceRegister.lock();
    for (int i = 0; i < IrisTracker_Count; i++) {
        if (my_devices_[i] != nullptr) {
            my_devices_[i]->RunFrame();
        }
    }
    mtx_deviceRegister.unlock();
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

IrisTrackerDevice* DeviceProvider::GetDevice(uint8_t index) {
    if (index >= IrisTracker_Count || index < 0) {
        std::stringstream stream;
        stream << "Attempted to get device out of range: 0x" << std::hex << index;
        vr::VRDriverLog()->Log(stream.str().c_str());
        return nullptr;
    }
    return my_devices_[index].get();
}

void DeviceProvider::InitTrackers() {
    json& conf = ClientConfig::Get();
    if (!conf.contains("active_trackers")) {
        conf["active_trackers"] = {
            { "head",        false },
            { "chest",       true  },
            { "hip",         true  },
            { "left_wrist",  false },
            { "right_wrist", false },
            { "left_elbow",  true  },
            { "right_elbow", true  },
            { "left_knee",   true  },
            { "right_knee",  true  },
            { "left_ankle",  true  },
            { "right_ankle", true  }
        };
    }

    mtx_deviceRegister.lock();
    for (uint8_t i = 0; i < IrisTracker_Count; i++) {
        if (my_devices_[i]) {
            my_devices_[i]->Register();
        }
        else {
            const string& key = IrisTracker_IndexMap.at(i);
            if (conf["active_trackers"].contains(key) &&
                conf["active_trackers"][key].is_boolean() &&
                conf["active_trackers"][key].get<bool>()) {
                my_devices_[i] = std::make_unique<IrisTrackerDevice>(i);
                my_devices_[i]->Register();
            }
        }
    }
    mtx_deviceRegister.unlock();
}