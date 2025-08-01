#pragma once
#include <nlohmann/json.hpp>
#include "util.h"
#include "device_provider.h"
using nlohmann::json;
using std::vector;

namespace IrisFBT {

	class IrisCalibrator
	{
	public:
		IrisCalibrator(DeviceProvider*);

		void on_pose(json&);
		void correct_pose(Mat4x4&);

	private:
		DeviceProvider* provider_;

		Mat4x4 mServerToDriver_;

		double left_wrist_pos_[3] = { 0, 0, 0 };
		long left_wrist_last_seen_ = -1;
		double right_wrist_pos_[3] = { 0, 0, 0 };
		long right_wrist_last_seen_ = -1;
		double head_pos_[3] = { 0, 0, 0 };
		long head_last_seen_ = -1;
	};

	extern std::unique_ptr<IrisCalibrator> iris_calib;
}
