#include "iris_tracker_device.h"
#include "../../lib/openvr/samples/drivers/utils/vrmath/vrmath.h"

IrisTrackerDevice::IrisTrackerDevice(vr::ETrackedControllerRole role) : role_(role), device_id_(vr::k_unTrackedDeviceIndexInvalid) {};

vr::EVRInitError IrisTrackerDevice::Activate(uint32_t unObjectId) {
    const vr::PropertyContainerHandle_t container = vr::VRProperties()->TrackedDeviceToPropertyContainer(unObjectId);
    vr::VRProperties()->SetInt32Property(container, vr::Prop_ControllerRoleHint_Int32, role_);
    vr::VRProperties()->SetStringProperty(container, vr::Prop_ModelNumber_String, iris_tracker_model);
    device_id_ = unObjectId;
    return vr::VRInitError_None;
}

void IrisTrackerDevice::RunFrame() {
	vr::VRServerDriverHost()->TrackedDevicePoseUpdated(device_id_, GetPose(), sizeof(vr::DriverPose_t));
}

void IrisTrackerDevice::Deactivate() {
}

void IrisTrackerDevice::EnterStandby() {
}

void* IrisTrackerDevice::GetComponent(const char* pchComponentNameAndVersion) {
    return nullptr;
}

void IrisTrackerDevice::DebugRequest(const char* pchRequest, char* pchResponseBuffer, uint32_t unResponseBufferSize) {
    if (unResponseBufferSize >= 1)
        pchResponseBuffer[0] = 0;
}

vr::DriverPose_t IrisTrackerDevice::GetPose() {
	vr::DriverPose_t pose = { 0 };

	pose.poseIsValid = true;
	pose.result = vr::TrackingResult_Running_OK;
	pose.deviceIsConnected = true;

	pose.qWorldFromDriverRotation.w = 1.f;
	pose.qDriverFromHeadRotation.w = 1.f;

	pose.qRotation.w = 1.f;

	vr::TrackedDevicePose_t hmd_pose{};
	vr::VRServerDriverHost()->GetRawTrackedDevicePoses(0.f, &hmd_pose, 1);

	if (hmd_pose.eTrackingResult != vr::TrackingResult_Running_OK) return pose;

	const vr::HmdQuaternion_t hmd_orientation = HmdQuaternion_FromMatrix(hmd_pose.mDeviceToAbsoluteTracking);
	pose.qRotation = hmd_orientation;

	pose.vecPosition[0] = role_ == vr::TrackedControllerRole_OptOut
		? hmd_pose.mDeviceToAbsoluteTracking.m[0][3]
		: role_ == vr::TrackedControllerRole_LeftHand
			? hmd_pose.mDeviceToAbsoluteTracking.m[0][3] - 0.2f
			: hmd_pose.mDeviceToAbsoluteTracking.m[0][3] + 0.2f;

	pose.vecPosition[1] = hmd_pose.mDeviceToAbsoluteTracking.m[1][3] - 0.5f;
	pose.vecPosition[2] = hmd_pose.mDeviceToAbsoluteTracking.m[2][3] - 0.25f;

	return pose;
}