#include "TFLoad.h"
#include <opencv2/dnn.hpp>
#include <opencv2/imgcodecs.hpp>
#include <opencv2/highgui.hpp>
#include <opencv2/cudacodec.hpp>
#include <iostream>
#include <string>

using namespace std;
using namespace cv;

dnn::Net net;

void GetModel() {
    // Load the model
    string path = WORKDIR_ + "Models\\tensorflow2\\movenet\\singlepose\\thunder-v4\\model.pb";
    cout << path << endl;
    net = dnn::readNetFromTensorflow(path);

    if (cuda::getCudaEnabledDeviceCount() > 0) {
        net.setPreferableBackend(dnn::DNN_BACKEND_CUDA);
    }

    /*cout << "layers:" << endl;
    for (string name : net.getLayerNames()) {
        cout << '\t' << name << " (";
        int id = net.getLayerId(name);
        cout << id << "):" << endl;
        
        vector<string> types;
        net.getLayerTypes(types);

        cout << "\t\ttypes:" << endl;
        for (string type : types) {
            cout << "\t\t\t" << type << endl;
        }

        vector<dnn::MatShape> shapes(types.size()), in_shapes, out_shapes;

        net.getLayerShapes(shapes, id, in_shapes, out_shapes);
    }*/
}

void RunModel(Mat image) {


    // Prepare the input
    //cv:: = cv::imread("path/to/image.jpg");
    Mat blob_NCHW = dnn::blobFromImage(image, 1.0, cv::Size(256, 256));

    int N = blob_NCHW.size[0];
    int C = blob_NCHW.size[1];
    int H = blob_NCHW.size[2];
    int W = blob_NCHW.size[3];

    int new_dims[] = { N, H, W, C };
    cv::Mat blob_NHWC(4, new_dims, blob_NCHW.type(), blob_NCHW.data);

    // Set the input blob
    net.setInput(blob_NHWC);

    // Forward pass
    Mat output = net.forward();

    int classId;
    double confidence;
    minMaxIdx(output, NULL, &confidence, NULL, &classId);

    std::cout << "Class ID: " << classId << ", Confidence: " << confidence << std::endl;
}