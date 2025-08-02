#pragma once
#include <nlohmann/json.hpp>
#include <openvr_driver.h>
using nlohmann::json;

namespace IrisFBT {
	struct Vector3 {
		double v[3];

		Vector3();
		Vector3(double, double, double);
		Vector3(json&);
		Vector3(vr::HmdMatrix34_t&);
		Vector3 operator*(double) const;
		Vector3 operator/(double) const;
		Vector3 operator+(const Vector3) const;
		Vector3 operator-(const Vector3) const;
		double operator*(const Vector3) const;

		double length() const;
	};

	struct Mat4x4 {
		double m[4][4];

		Mat4x4();
		Mat4x4(json&);
		Mat4x4 operator*(const Mat4x4) const;
		Vector3 operator*(const Vector3) const;
	};

	vr::HmdQuaternion_t mRot2Quat(Mat4x4);
}