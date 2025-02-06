#include "TFLoad.h"
#include <opencv2/dnn.hpp>
#include <opencv2/imgcodecs.hpp>
#include <opencv2/highgui.hpp>
#include <iostream>

using namespace std;
using namespace cv;
using namespace dnn;

Net net;

void GetModel(bool is_cuda) {
	// Load the model
	net = readNet("C:\\Users\\User\\source\\repos\\Iris-Full-Body-Tracking\\Models\\onnx\\yolo11n-pose.onnx");
	
	if (is_cuda)
	{
		cout << "Using CUDA\n";
		net.setPreferableBackend(cv::dnn::DNN_BACKEND_CUDA);
		net.setPreferableTarget(cv::dnn::DNN_TARGET_CUDA_FP16);
	}
	else
	{
		cout << "CPU Mode\n";
		net.setPreferableBackend(cv::dnn::DNN_BACKEND_OPENCV);
		net.setPreferableTarget(cv::dnn::DNN_TARGET_CPU);
	}
}

void RunModel(Mat image) {

	// Prepare the input
	Mat blob = blobFromImage(image, 1./255., cv::Size(640, 640), cv::Scalar(), true);

	// Set the input blob
	net.setInput(blob);

	// Forward pass
	Mat output = net.forward();

	/*int classId;
	double confidence;
	minMaxIdx(output, NULL, &confidence, NULL, &classId);

	std::cout << "Class ID: " << classId << ", Confidence: " << confidence << std::endl;*/
}