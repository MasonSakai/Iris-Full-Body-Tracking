#pragma once

#include "CameraData.h"
#include <opencv2/core.hpp>
#include <opencv2/calib3d.hpp>
#include <opencv2/core/utility.hpp>

using namespace std;

class Settings
{
public:
	Settings() : goodInput(false) {}

	void write(cv::FileStorage& fs) const                        //Write serialization for this class
	{
		fs << "{"
			<< "BoardSize_Width" << boardSize.width
			<< "BoardSize_Height" << boardSize.height
			<< "Square_Size" << squareSize
			<< "Marker_Size" << markerSize
			<< "ArUco_Dict" << arucoDictID
			<< "Calibrate_FixAspectRatio" << aspectRatio
			<< "Calibrate_AssumeZeroTangentialDistortion" << calibZeroTangentDist
			<< "Calibrate_FixPrincipalPointAtTheCenter" << calibFixPrincipalPoint

			<< "Write_DetectedFeaturePoints" << writePoints
			<< "Write_extrinsicParameters" << writeExtrinsics
			<< "Write_gridPoints" << writeGrid

			<< "Show_UndistortedImage" << showUndistorted

			<< "Input_FlipAroundHorizontalAxis" << flipVertical
			<< "}";
	}
	void read(const cv::FileNode& node)                          //Read serialization for this class
	{
		node["BoardSize_Width"] >> boardSize.width;
		node["BoardSize_Height"] >> boardSize.height;
		node["Square_Size"] >> squareSize;
		node["Marker_Size"] >> markerSize;
		node["ArUco_Dict"] >> arucoDictID;
		node["Calibrate_FixAspectRatio"] >> aspectRatio;
		node["Write_DetectedFeaturePoints"] >> writePoints;
		node["Write_extrinsicParameters"] >> writeExtrinsics;
		node["Write_gridPoints"] >> writeGrid;
		node["Calibrate_AssumeZeroTangentialDistortion"] >> calibZeroTangentDist;
		node["Calibrate_FixPrincipalPointAtTheCenter"] >> calibFixPrincipalPoint;
		node["Calibrate_UseFisheyeModel"] >> useFisheye;
		node["Input_FlipAroundHorizontalAxis"] >> flipVertical;
		node["Show_UndistortedImage"] >> showUndistorted;
		node["Fix_K1"] >> fixK1;
		node["Fix_K2"] >> fixK2;
		node["Fix_K3"] >> fixK3;
		node["Fix_K4"] >> fixK4;
		node["Fix_K5"] >> fixK5;

		validate();
	}
	void validate()
	{
		goodInput = true;
		if (boardSize.width <= 0 || boardSize.height <= 0)
		{
			cerr << "Invalid Board size: " << boardSize.width << " " << boardSize.height << endl;
			goodInput = false;
		}
		if (squareSize <= 10e-6)
		{
			cerr << "Invalid square size " << squareSize << endl;
			goodInput = false;
		}

		flag = 0;
		if (calibFixPrincipalPoint) flag |= cv::CALIB_FIX_PRINCIPAL_POINT;
		if (calibZeroTangentDist)   flag |= cv::CALIB_ZERO_TANGENT_DIST;
		if (aspectRatio)            flag |= cv::CALIB_FIX_ASPECT_RATIO;
		if (fixK1)                  flag |= cv::CALIB_FIX_K1;
		if (fixK2)                  flag |= cv::CALIB_FIX_K2;
		if (fixK3)                  flag |= cv::CALIB_FIX_K3;
		if (fixK4)                  flag |= cv::CALIB_FIX_K4;
		if (fixK5)                  flag |= cv::CALIB_FIX_K5;

		if (useFisheye) {
			// the fisheye model has its own enum, so overwrite the flags
			flag = cv::fisheye::CALIB_FIX_SKEW | cv::fisheye::CALIB_RECOMPUTE_EXTRINSIC;
			if (fixK1)                   flag |= cv::fisheye::CALIB_FIX_K1;
			if (fixK2)                   flag |= cv::fisheye::CALIB_FIX_K2;
			if (fixK3)                   flag |= cv::fisheye::CALIB_FIX_K3;
			if (fixK4)                   flag |= cv::fisheye::CALIB_FIX_K4;
			if (calibFixPrincipalPoint) flag |= cv::fisheye::CALIB_FIX_PRINCIPAL_POINT;
		}
		atImageList = 0;
	}
	cv::Mat nextImage()
	{
		cv::Mat result;
		if (atImageList < imageList.size())
			result = *imageList.at(atImageList++);

		return result;
	}

	~Settings() {
		for (auto img : imageList) delete img;
	}
public:
	cv::Size boardSize = { 5, 7 };   // The size of the board -> Number of items by width and height
	float squareSize = 30;       // The size of a square in your defined unit (point, millimeter,etc).
	float markerSize = 15;       // The size of a marker in your defined unit (point, millimeter,etc).
	int arucoDictID = 10;        // ID of preexisting dictionary
	float aspectRatio;           // The aspect ratio
	bool writePoints;            // Write detected feature points
	bool writeExtrinsics;        // Write extrinsic parameters
	bool writeGrid;              // Write refined 3D target grid points
	bool calibZeroTangentDist;   // Assume zero tangential distortion
	bool calibFixPrincipalPoint; // Fix the principal point at the center
	bool flipVertical;           // Flip the captured images around the horizontal axis
	bool showUndistorted;        // Show undistorted images after calibration
	bool useFisheye;             // use fisheye camera model for calibration
	bool fixK1;                  // fix K1 distortion coefficient
	bool fixK2;                  // fix K2 distortion coefficient
	bool fixK3;                  // fix K3 distortion coefficient
	bool fixK4;                  // fix K4 distortion coefficient
	bool fixK5;                  // fix K5 distortion coefficient

	CalibrationData calibData;
	vector<cv::Mat*> imageList;
	size_t atImageList;
	bool goodInput;
	int flag;
};

bool PerformCalibration(Settings& s);
void App_CalibrateCamera(int camIndex, CameraData* camData);