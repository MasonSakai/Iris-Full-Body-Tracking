#pragma once

#include "openvr_driver.h"
#include "device_data_refs.h"

namespace IrisFBT {

    class IrisTrackerDevice : public vr::ITrackedDeviceServerDriver {
    public:
        IrisTrackerDevice(IrisTrackerIndex index);

        // Inherited via ITrackedDeviceServerDriver
        virtual void Register();
        virtual vr::EVRInitError Activate(uint32_t unObjectId) override;
        virtual void Deactivate() override;
        void RunFrame();
        virtual void EnterStandby() override;
        virtual void* GetComponent(const char* pchComponentNameAndVersion) override;
        virtual void DebugRequest(const char* pchRequest, char* pchResponseBuffer, uint32_t unResponseBufferSize) override;
        virtual vr::DriverPose_t GetPose() override;

    private:
        vr::TrackedDeviceIndex_t device_id_;
        IrisTrackerIndex device_index_;
    };
}