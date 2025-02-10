#include "TFLoad.h"
#include <opencv2/dnn.hpp>
#include <opencv2/imgcodecs.hpp>
#include <opencv2/highgui.hpp>
#include <iostream>

#include <YOLO11.hpp>

using namespace std;
using namespace cv;
using namespace dnn;

YOLO11Detector* detector;

void GetModel(bool isGPU) {
	cout << "Getting Detector" << endl;
	auto modelPath = "C:\\Users\\User\\source\\repos\\Iris-Full-Body-Tracking\\Models\\onnx\\yolo11n-pose.onnx";
	detector = new YOLO11Detector(modelPath, "", isGPU);
	cout << "Started Detector" << endl;
}

void RunModel(Mat image) {

	vector<Detection> detections = detector->detect(image);


}