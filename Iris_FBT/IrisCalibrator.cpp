#include "IrisCalibrator.h"
#include <openvr_driver.h>

using namespace IrisFBT;

namespace IrisFBT {
	std::unique_ptr<IrisCalibrator> iris_calib = nullptr;
}

IrisFBT::IrisCalibrator::IrisCalibrator(DeviceProvider* provider) : provider_(provider) {}

void IrisCalibrator::on_pose(json& pose) {
	//vr::VRServerDriverHost()->GetRawTrackedDevicePoses(0.f, )
}

void IrisCalibrator::correct_pose(Mat4x4& mat) {
	mat = iris_calib->mServerToDriver_ * mat;
}