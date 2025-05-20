#pragma once

extern const char* iris_tracker_serial;
extern const char* iris_tracker_model;

typedef enum {
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