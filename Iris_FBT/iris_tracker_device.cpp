#include "iris_tracker_device.h"
#include "device_provider.h"
#include "../lib/openvr/samples/drivers/utils/vrmath/vrmath.h"
#include "IrisCalibrator.h"
using namespace IrisFBT;

IrisTrackerDevice::IrisTrackerDevice(uint8_t index) : device_id_(vr::k_unTrackedDeviceIndexInvalid), device_index_((IrisTrackerIndex)index) {};

void IrisTrackerDevice::Register() {
	vr::VRServerDriverHost()->TrackedDeviceAdded((iris_tracker_serial + IrisTracker_IndexMap.at(device_index_)).c_str(),
		vr::TrackedDeviceClass_GenericTracker, this);
}

vr::EVRInitError IrisTrackerDevice::Activate(uint32_t unObjectId) {
	const vr::PropertyContainerHandle_t container = vr::VRProperties()->TrackedDeviceToPropertyContainer(unObjectId);
	vr::VRProperties()->SetStringProperty(container, vr::Prop_ModelNumber_String, iris_tracker_model);
	device_id_ = unObjectId;
	return vr::VRInitError_None;
}

void IrisTrackerDevice::Deactivate() {
}

void IrisTrackerDevice::RunFrame() {
	//vr::VRServerDriverHost()->TrackedDevicePoseUpdated(device_id_, GetPose(), sizeof(vr::DriverPose_t));
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
	vr::VRDriverLog()->Log("Get Pose");
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

	pose.vecPosition[0] = hmd_pose.mDeviceToAbsoluteTracking.m[0][3];
	pose.vecPosition[1] = hmd_pose.mDeviceToAbsoluteTracking.m[1][3] - 0.5f;
	pose.vecPosition[2] = hmd_pose.mDeviceToAbsoluteTracking.m[2][3] - 0.25f;

	return pose;
}

void IrisTrackerDevice::UpdatePose(Mat4x4 data) {
	vr::DriverPose_t pose = { 0 };

	pose.poseIsValid = true;
	pose.result = vr::TrackingResult_Running_OK;
	pose.deviceIsConnected = true;

	pose.qWorldFromDriverRotation.w = 1.f;
	pose.qDriverFromHeadRotation.w = 1.f;

	iris_calib->correct_pose(data);

	pose.qRotation = mRot2Quat(data);

	pose.vecPosition[0] = data.m[0][3];
	pose.vecPosition[1] = data.m[1][3];
	pose.vecPosition[2] = data.m[2][3];

	latest_pose_ = pose;
	vr::VRServerDriverHost()->TrackedDevicePoseUpdated(device_id_, pose, sizeof(vr::DriverPose_t));
}

void IrisTrackerDevice::UpdatePoseEmpty() {
	vr::DriverPose_t pose = { 0 };

	pose.poseIsValid = false;
	pose.result = vr::TrackingResult_Running_OutOfRange;
	pose.deviceIsConnected = true;

	latest_pose_ = pose;
	vr::VRServerDriverHost()->TrackedDevicePoseUpdated(device_id_, pose, sizeof(vr::DriverPose_t));
}