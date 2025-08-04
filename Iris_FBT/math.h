#pragma once
#include <nlohmann/json.hpp>
#include <openvr_driver.h>
using nlohmann::json;
using std::string;

const double PI = 3.14159265358979323846;

namespace IrisFBT {
	struct Vector3 {
		double v[3];

		Vector3();
		Vector3(double, double, double);
		Vector3(json&);
		Vector3(vr::HmdMatrix34_t&);
		Vector3 operator*(double) const;
		Vector3 operator*=(double);
		Vector3 operator/(double) const;
		Vector3 operator/=(double);
		Vector3 operator+(const Vector3) const;
		Vector3 operator+=(const Vector3);
		Vector3 operator-(const Vector3) const;
		Vector3 operator-() const;
		Vector3 operator-=(const Vector3);
		double operator*(const Vector3) const;

		static double dot(const Vector3, const Vector3);
		static Vector3 cross(const Vector3, const Vector3);
		static Vector3 project(const Vector3, const Vector3);
		static Vector3 reject(const Vector3, const Vector3);
		Vector3 normalized() const;
		double length() const;
		double len2() const;

		string to_string() const;

	};

	struct Mat3x3 {
		double m[3][3];

		Mat3x3();
		Mat3x3(int);
		Mat3x3(json&);
		Mat3x3(const Vector3, const Vector3, const Vector3);
		Mat3x3(const vr::HmdQuaternion_t);
		Mat3x3 operator*(const Mat3x3) const;
		Vector3 operator*(const Vector3) const;
		void CopyQuat(const vr::HmdQuaternion_t);
		Vector3 get_vector(int) const;
		void set_vector(const Vector3, int);
		Mat3x3 transpose() const;
		double determinant() const;

		string to_string() const;
	};

	struct Mat4x4 {
		double m[4][4];

		Mat4x4();
		Mat4x4(int);
		Mat4x4(json&);
		Mat4x4(const Mat3x3, const Vector3);
		Mat4x4(const vr::HmdQuaternion_t, const Vector3);
		Mat4x4 operator*(const Mat4x4) const;
		Vector3 operator*(const Vector3) const;
		Mat4x4 inverse() const;
		Mat3x3 get_rotation() const;
		Vector3 get_vector(int = 3) const;
		void set_vector(const Vector3, int = 3);

		string to_string() const;
		json to_json() const;
	};

	vr::HmdQuaternion_t mRot2Quat(const Mat3x3&);
	string quat_to_string(vr::HmdQuaternion_t&);

	Vector3 computePlaneNormal(const Vector3[], const int);
	Mat3x3 refineRotationKabsch(const Vector3[], const Vector3[], int);
	double rotationDifferenceAngle(const Mat3x3&, const Mat3x3&);
	void estimateLocalOffsetAndTranslation(
		Vector3 src_pos_list[], Vector3 dst_pos_list[],
		Vector3 src_dir_list[], Vector3 dst_dir_list[],
		Vector3 src_norm, Vector3 dst_norm, int N,
		Vector3& outLocalOffset,
		Vector3& outTranslation
	);

}