#include "device_data_refs.h"

namespace IrisFBT {

	const char* iris_tracker_serial = "iris_serial_";
	const char* iris_tracker_model = "Iris VR Driver 1.0.0";

	const std::string iris_tracker_name_prefix = "IrisTracker_";

	const std::map<uint8_t, const std::string> IrisTracker_IndexMap = {
		{ IrisTracker_Head,        "head"        },
		{ IrisTracker_Chest,       "chest"       },
		{ IrisTracker_Hip,         "hip"         },
		{ IrisTracker_Hand_Left,   "left_wrist"  },
		{ IrisTracker_Hand_Right,  "right_wrist" },
		{ IrisTracker_Elbow_Left,  "left_elbow"  },
		{ IrisTracker_Elbow_Right, "right_elbow" },
		{ IrisTracker_Knee_Left,   "left_knee"   },
		{ IrisTracker_Knee_Right,  "right_knee"  },
		{ IrisTracker_Foot_Left,   "left_ankle"  },
		{ IrisTracker_FootRight,   "right_ankle" }
	};
}