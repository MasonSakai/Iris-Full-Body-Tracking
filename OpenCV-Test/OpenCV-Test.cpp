#include <opencv2/core.hpp>
#include <opencv2/imgcodecs.hpp>
#include <opencv2/highgui.hpp>
#include <iostream>
#include "CameraEnum.h"
#include "TFLoad.h"

using namespace cv;
using namespace std;

const vector<int> params = { CAP_PROP_FRAME_WIDTH, 640, CAP_PROP_FRAME_HEIGHT, 640, CAP_PROP_FPS, 90 };

int main(int argc, char** argv)
{
    GetCams();

    GetModel();

    VideoCapture cap;

    cap.open(0, CAP_ANY, params);

    if (!cap.isOpened()) {
        cerr << "ERROR! Unable to open camera\n";
        return -1;
    }

    cout << "Backend: " << cap.get(CAP_PROP_BACKEND) << ", " << cap.getBackendName() << endl;
    cout << "FPS: " << cap.get(CAP_PROP_FPS) << endl;

    Mat frame;
    //--- GRAB AND WRITE LOOP
    cout << "Start grabbing" << endl
         << "Press any key to terminate" << endl;
    for (;;)
    {
        // wait for a new frame from camera and store it into 'frame'
        cap.read(frame);
        // check if we succeeded
        if (frame.empty()) {
            cerr << "ERROR! blank frame grabbed\n";
            break;
        }
        // show live and wait for a key with timeout long enough to show images
        imshow("Live", frame);
        RunModel(frame);
        break;
        if (pollKey() >= 0)
            break;
    }
    // the camera will be deinitialized automatically in VideoCapture destructor
    return 0;
}