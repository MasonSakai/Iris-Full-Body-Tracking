#pragma once

#include "openvr_driver.h"
#include "device_data_refs.h"
using std::vector;

namespace IrisFBT {

    class IrisTrackerDevice : public vr::ITrackedDeviceServerDriver {
    public:
        IrisTrackerDevice(uint8_t index);

        // Inherited via ITrackedDeviceServerDriver
        virtual void Register();
        virtual vr::EVRInitError Activate(uint32_t unObjectId) override;
        virtual void Deactivate() override;
        void RunFrame();
        virtual void EnterStandby() override;
        virtual void* GetComponent(const char* pchComponentNameAndVersion) override;
        virtual void DebugRequest(const char* pchRequest, char* pchResponseBuffer, uint32_t unResponseBufferSize) override;
        virtual vr::DriverPose_t GetPose() override;
        void UpdatePose(vector<vector<double>>);
        void UpdatePoseEmpty();

    private:
        vr::TrackedDeviceIndex_t device_id_;
        IrisTrackerIndex device_index_;

        vr::DriverPose_t latest_pose_;
    };
}