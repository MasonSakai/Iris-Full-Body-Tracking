mkdir build
cd build
cmake ../opencv
cmake -D OPENCV_EXTRA_MODULES_PATH=../opencv_contrib/modules ../opencv
cmake --build .