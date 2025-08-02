#include "IrisCalibrator.h"
#include <openvr_driver.h>
#include <string>
using std::string;

using namespace IrisFBT;

namespace IrisFBT {
	std::unique_ptr<IrisCalibrator> iris_calib = nullptr;
}

IrisFBT::IrisCalibrator::IrisCalibrator(DeviceProvider* provider) : provider_(provider) {}

void IrisCalibrator::RecacheDevices() {
	if (last_recache_ < next_recache_) {
		last_recache_++;
	}
	else {
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

		next_recache_ = (hmd_index == -1 || hand_left_index == -1 || hand_right_index == -1) ? 0x0100U : 0x1000U;

		if (hmd_poses != nullptr)
			delete[] hmd_poses;
		hmd_poses = new vr::TrackedDevicePose_t[max_index];
	}
	if (max_index != 0) vr::VRServerDriverHost()->GetRawTrackedDevicePoses(0.f, hmd_poses, max_index);
}

static bool CheckArm(Vector3 pos_wrist, string key_elbow, string key_shoulder, json& pose) {
	if (!pose.contains(key_elbow) || !pose.contains(key_shoulder)) return false;
	Vector3 pos_elbow = pose[key_elbow];
	Vector3 pos_shoulder = pose[key_shoulder];

	double dot = (pos_wrist - pos_elbow) * (pos_elbow - pos_shoulder);
	dot /= (pos_wrist - pos_elbow).length() * (pos_elbow - pos_shoulder).length();
	return dot > 0.9;
}

static bool CheckChest(Vector3 pos_wrist_left, Vector3 pos_wrist_right, string key_chest, json& pose) {
	if (!pose.contains(key_chest)) return false;
	Vector3 pos_chest = pose[key_chest];

	double dot = (pos_wrist_left - pos_chest) * (pos_wrist_right - pos_chest);
	dot /= (pos_wrist_left - pos_chest).length() * (pos_wrist_right - pos_chest).length();
	return dot < -0.92;
}

void IrisCalibrator::on_pose(json& pose) {
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

	if (!is_calibrating) return;
	if (last_seen_head_ > 5 || last_seen_left_wrist_ > 5 || last_seen_right_wrist_ > 5) return;

	if (max_index == 0) return;
	if (hand_left_index == -1 || hand_right_index == -1) return;

	if (hmd_poses[hand_left_index].eTrackingResult != vr::TrackingResult_Running_OK ||
		hmd_poses[hand_right_index].eTrackingResult != vr::TrackingResult_Running_OK) return;
	if (!hmd_poses[hand_left_index].bPoseIsValid ||
		!hmd_poses[hand_right_index].bPoseIsValid) return;

	if (!CheckArm(pos_left_wrist_, "left_elbow", "left_shoulder", pose)) return;
	if (!CheckArm(pos_right_wrist_, "right_elbow", "right_shoulder", pose)) return;
	if (!CheckChest(pos_left_wrist_, pos_right_wrist_, "chest", pose)) return;

	Vector3 pos_hand_left = hmd_poses[hand_left_index].mDeviceToAbsoluteTracking;
	Vector3 pos_hand_right = hmd_poses[hand_right_index].mDeviceToAbsoluteTracking;

	double dist_hands = (pos_hand_right - pos_hand_left).length();
	double dist_wrists = (pos_right_wrist_ - pos_left_wrist_).length();

	if (abs((dist_hands / dist_wrists) - 1.2) > 0.175) return;


	Vector3 dir_vr = (pos_hand_right - pos_hand_left).normalized();
	Vector3 dir_iris = (pos_right_wrist_ - pos_left_wrist_).normalized();

	double dot;
	for (int i = 0; i < calib_list_index_; i++) {
		dot = calib_dir_list_vr_[i] * dir_vr;
		if (abs(dot) > 0.999) return;
		dot = calib_dir_list_iris_[i] * dir_iris;
		if (abs(dot) > 0.999) return;
	}
	vr::VRDriverLog()->Log(("calib: " + std::to_string(calib_list_index_)).c_str());

	calib_dir_list_vr_[calib_list_index_] = dir_vr;
	calib_dir_list_iris_[calib_list_index_] = dir_iris;
	calib_pos_list_vr_[calib_list_index_] = (pos_hand_right + pos_hand_left) / 2;
	calib_pos_list_iris_[calib_list_index_] = (pos_right_wrist_ + pos_left_wrist_) / 2;
	calib_list_index_++;

	if (calib_list_index_ >= k_unCalibListLen) {
		is_calibrating = false;

		Vector3 norm_vr_ref = Vector3::cross(calib_dir_list_vr_[1], calib_dir_list_vr_[0]).normalized();
		Vector3 norm_iris_ref = Vector3::cross(calib_dir_list_iris_[1], calib_dir_list_iris_[0]).normalized();
		Vector3 norm_vr, norm_iris, tmp;
		int n = 0;
		for (int i = 1; i < k_unCalibListLen; i++) {
			for (int j = 0; j < i; j++) {
				n++;
				tmp = Vector3::cross(calib_dir_list_vr_[i], calib_dir_list_vr_[j]).normalized();
				if (norm_vr_ref * tmp < 0) tmp *= -1;
				norm_vr += tmp;
				tmp = Vector3::cross(calib_dir_list_iris_[i], calib_dir_list_iris_[j]).normalized();
				if (norm_iris_ref * tmp < 0) tmp *= -1;
				norm_iris += tmp;
			}
		}
		norm_vr /= n;
		norm_iris /= n;

		Mat4x4 mats[k_unCalibListLen];
		for (int i = 0; i < k_unCalibListLen; i++) {
			Vector3 dir_vr = Vector3::reject(calib_dir_list_vr_[i], norm_vr).normalized();
			Mat4x4 mat_vr(dir_vr, norm_vr, Vector3::cross(dir_vr, norm_vr), Vector3());

			Vector3 dir_iris = Vector3::reject(calib_dir_list_iris_[i], norm_iris).normalized();
			Mat4x4 mat_iris(dir_iris, norm_iris, Vector3::cross(dir_iris, norm_iris), Vector3());

			mats[i] = mat_vr * mat_iris.inverse();

			vr::VRDriverLog()->Log(("calib mat " + mats[i].to_string()).c_str());
		}

		mServerToDriver_ = mats[0];

		vr::VRDriverLog()->Log(("calib complete " + norm_vr.to_string() + ", " + norm_iris.to_string()).c_str());
	}
}

void IrisCalibrator::correct_pose(Mat4x4& mat) {
	mat = iris_calib->mServerToDriver_ * mat;
}