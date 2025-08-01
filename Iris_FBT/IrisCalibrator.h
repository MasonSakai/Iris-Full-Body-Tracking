#pragma once
#include <nlohmann/json.hpp>
using nlohmann::json;

namespace Iris_FBT {

	static class IrisCalibrator
	{
	public:

		void on_pose(json&);

	private:


		double left_wrist_pos_[3] = { 0, 0, 0 };
		long left_wrist_last_seen_ = -1;
		double right_wrist_pos_[3] = { 0, 0, 0 };
		long right_wrist_last_seen_ = -1;
		double head_pos_[3] = { 0, 0, 0 };
		long head_last_seen_ = -1;
	};

}
