#include "IrisCalibrator.h"
#include <openvr_driver.h>
#include <string>
using std::string;

using namespace IrisFBT;

namespace IrisFBT {
	std::unique_ptr<IrisCalibrator> iris_calib = nullptr;
}

IrisFBT::IrisCalibrator::IrisCalibrator(DeviceProvider* provider) : provider_(provider) {}


unsigned short last_recache_ = -1;
uint32_t max_index = 0;
vr::TrackedDevicePose_t* hmd_poses = nullptr;
uint32_t hmd_index = -1, hand_left_index = -1, hand_right_index = -1;
static void RecacheDevices() {
	if (last_recache_ < 500U) {
		last_recache_++;
		return;
	}
	vr::VRDriverLog()->Log("Recache");
	last_recache_ = 0;
	max_index = 0;
	hmd_index = -1;
	hand_left_index = -1;
	hand_right_index = -1;

	for (uint32_t i = 0; i < vr::k_unMaxTrackedDeviceCount; i++) {
		auto handle = vr::VRProperties()->TrackedDeviceToPropertyContainer(i);
		vr::ETrackedPropertyError err;
		auto prop = vr::VRProperties()->GetInt32Property(handle, vr::Prop_DeviceClass_Int32, &err);

		if (err != vr::TrackedProp_Success) continue;

		if (prop == vr::TrackedDeviceClass_HMD) {
			hmd_index = i;
			max_index = i + 1;
		}
		else if (prop == vr::TrackedDeviceClass_Controller) {
			auto role = vr::VRProperties()->GetInt32Property(handle, vr::Prop_ControllerRoleHint_Int32, &err);
			if (role == vr::TrackedControllerRole_LeftHand) {
				hand_left_index = i;
				max_index = i + 1;
			}
			else if (role == vr::TrackedControllerRole_RightHand) {
				hand_right_index = i;
				max_index = i + 1;
			}
		}
	}

	if (hmd_poses != nullptr)
		delete[] hmd_poses;
	hmd_poses = new vr::TrackedDevicePose_t[max_index];
}

static bool CheckArm(Vector3 pos_wrist, string key_elbow, string key_shoulder, json& pose) {
	if (!pose.contains(key_elbow) || !pose.contains(key_shoulder)) return false;
	Vector3 pos_elbow = pose[key_elbow];
	Vector3 pos_shoulder = pose[key_shoulder];

	double dot = (pos_wrist - pos_elbow) * (pos_elbow - pos_shoulder);
	dot /= (pos_wrist - pos_elbow).length() * (pos_elbow - pos_shoulder).length();
	return dot > 0.92;
}

static bool CheckChest(Vector3 pos_wrist_left, Vector3 pos_wrist_right, string key_chest, json& pose) {
	if (!pose.contains(key_chest)) return false;
	Vector3 pos_chest = pose[key_chest];

	double dot = (pos_wrist_left - pos_chest) * (pos_wrist_right - pos_chest);
	dot /= (pos_wrist_left - pos_chest).length() * (pos_wrist_right - pos_chest).length();
	return dot < -0.92;
}

void IrisCalibrator::on_pose(json& pose) {
	RecacheDevices();

	last_seen_head_++;
	last_seen_left_wrist_++;
	last_seen_right_wrist_++;

	if (pose.contains("head")) {
		pos_head_ = pose["head"];
		last_seen_head_ = 0;
	}
	if (pose.contains("left_wrist")) {
		pos_left_wrist_ = pose["left_wrist"];
		last_seen_left_wrist_ = 0;
	}
	if (pose.contains("right_wrist")) {
		pos_right_wrist_ = pose["right_wrist"];
		last_seen_right_wrist_ = 0;
	}

	if (last_seen_head_ > 5 || last_seen_left_wrist_ > 5 || last_seen_right_wrist_ > 5) return;

	if (max_index == 0) return;
	if (hmd_index == -1 || hand_left_index == -1 || hand_right_index == -1) return;

	vr::VRServerDriverHost()->GetRawTrackedDevicePoses(0.f, hmd_poses, max_index);
	if (hmd_poses[hmd_index].eTrackingResult != vr::TrackingResult_Running_OK ||
		hmd_poses[hand_left_index].eTrackingResult != vr::TrackingResult_Running_OK ||
		hmd_poses[hand_right_index].eTrackingResult != vr::TrackingResult_Running_OK) return;
	if (!hmd_poses[hmd_index].bPoseIsValid ||
		!hmd_poses[hand_left_index].bPoseIsValid ||
		!hmd_poses[hand_right_index].bPoseIsValid) return;

	if (!CheckArm(pos_left_wrist_, "left_elbow", "left_shoulder", pose)) return;
	if (!CheckArm(pos_right_wrist_, "right_elbow", "right_shoulder", pose)) return;
	if (!CheckChest(pos_left_wrist_, pos_right_wrist_, "chest", pose)) return;

	Vector3 pos_hmd = hmd_poses[hmd_index].mDeviceToAbsoluteTracking;
	Vector3 pos_hand_left = hmd_poses[hand_left_index].mDeviceToAbsoluteTracking;
	Vector3 pos_hand_right = hmd_poses[hand_right_index].mDeviceToAbsoluteTracking;

	Vector3 midPos_vr = (pos_hand_right + pos_hand_left) / 2;
	double dist_hmd = (pos_hmd - midPos_vr).length();
	double dist_hands = (pos_hand_right - pos_hand_left).length();

	Vector3 midPos = (pos_right_wrist_ + pos_left_wrist_) / 2;
	double dist_head = (pos_head_ - midPos).length();
	double dist_wrists = (pos_right_wrist_ - pos_left_wrist_).length();

	vr::VRDriverLog()->Log(("calib: " + std::to_string(dist_hmd - dist_head) + ", " + std::to_string(dist_hands - dist_wrists)).c_str());
}

void IrisCalibrator::correct_pose(Mat4x4& mat) {
	mat = iris_calib->mServerToDriver_ * mat;
}