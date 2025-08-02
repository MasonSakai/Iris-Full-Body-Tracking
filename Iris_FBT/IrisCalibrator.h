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

		void on_pose(json&);
		void correct_pose(Mat4x4&);

	private:
		DeviceProvider* provider_;

		Mat4x4 mServerToDriver_;

		Vector3 pos_left_wrist_;
		unsigned long last_seen_left_wrist_ = 0;
		Vector3 pos_right_wrist_;
		unsigned long last_seen_right_wrist_ = 0;
		Vector3 pos_head_;
		unsigned long last_seen_head_ = 0;
	};

	extern std::unique_ptr<IrisCalibrator> iris_calib;
}
