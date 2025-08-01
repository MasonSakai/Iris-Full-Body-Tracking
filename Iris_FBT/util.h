#pragma once
#include <vector>
#include <string>
#include <nlohmann/json.hpp>
#include <sio_client.h>
#include <openvr_driver.h>
using nlohmann::json;
using std::string;
using std::wstring;
using std::vector;

namespace IrisFBT {

	wstring getAppdata();
	wstring getDriverPath();

	vector<string> split(const string& text, char delimiter);

	json messageToJson(sio::message::ptr);

	struct Mat4x4 {
		double m[4][4];

		Mat4x4();
		Mat4x4(json& data);
		const Mat4x4 operator*(const Mat4x4);
	};

	vr::HmdQuaternion_t mRot2Quat(Mat4x4);
}
