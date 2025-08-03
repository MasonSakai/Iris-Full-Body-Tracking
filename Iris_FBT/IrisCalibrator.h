#pragma once
#include <nlohmann/json.hpp>
#include "math.h"
#include "device_provider.h"
using nlohmann::json;
using std::vector;

namespace IrisFBT {

	class IrisCalibrator
	{
	public:
		IrisCalibrator(DeviceProvider*);

		void RecacheDevices();

		void on_pose(json&);
		void correct_pose(Mat4x4&);

		bool is_calibrating = true;

	private:
		DeviceProvider* provider_;

		Mat4x4 mServerToDriver_;

		Vector3 pos_left_wrist_;
		unsigned long last_seen_left_wrist_ = 0;
		Vector3 pos_right_wrist_;
		unsigned long last_seen_right_wrist_ = 0;
		Vector3 pos_head_;
		unsigned long last_seen_head_ = 0;

		static const uint32_t k_unCalibListLen = 20;

		unsigned short last_recache_ = -1;
		unsigned short next_recache_ = 0x0040U;
		uint32_t max_index = 0;
		vr::TrackedDevicePose_t* hmd_poses = nullptr;
		uint32_t hmd_index = -1, hand_left_index = -1, hand_right_index = -1;

		int calib_list_index_ = 0;
		Vector3 calib_dir_list_vr_[k_unCalibListLen];
		Vector3 calib_pos_list_vr_[k_unCalibListLen];
		Vector3 calib_dir_list_iris_[k_unCalibListLen];
		Vector3 calib_pos_list_iris_[k_unCalibListLen];

		void Calibrate();
	};

	extern std::unique_ptr<IrisCalibrator> iris_calib;
}
