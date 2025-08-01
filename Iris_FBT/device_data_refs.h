#pragma once
#include <map>
#include <string>

namespace IrisFBT {

	extern const char* iris_tracker_serial;
	extern const char* iris_tracker_model;

	typedef enum: uint8_t {
		IrisTracker_Head,
		IrisTracker_Chest,
		IrisTracker_Hip,
		IrisTracker_Hand_Left,
		IrisTracker_Hand_Right,
		IrisTracker_Elbow_Left,
		IrisTracker_Elbow_Right,
		IrisTracker_Knee_Left,
		IrisTracker_Knee_Right,
		IrisTracker_Foot_Left,
		IrisTracker_FootRight,
		IrisTracker_Count
	} IrisTrackerIndex;

	extern const std::map<uint8_t, const std::string> IrisTracker_IndexMap;
}