#include "CameraData.h"
#include <opencv2/core/persistence.hpp>
#include <iostream>

using namespace cv;

void StringSplit(string str, string delimiter, vector<string>* split) {
	int ind = 0, p = 0;
	while (p >= 0) {
		p = str.find(delimiter, ind);
		string s = str.substr(ind, p - ind);
		split->push_back(s);
		ind = p + 1;
	}
}


static vector<CameraData>* cameraData;
static vector<CameraPrefab>* cameraPrefabs;



static void ReadAddress(FileNode node, USBDeviceAddress* address) {
	if (node.empty()) return;

	address->VendorID = (int)node["vendor"];
	address->ProductID = (int)node["product"];

	FileNode interfaceNum = node["interfaceNum"];
	if (interfaceNum.isInt()) address->interfaceNum = (int)interfaceNum;

	FileNode serialString = node["serialString"];
	if (!serialString.isNone()) address->serialString = serialString;
}
static void WriteAddress(FileStorage& fs, USBDeviceAddress& address) {
	fs << "{";
	fs << "vendor" << address.VendorID;
	fs << "product" << address.ProductID;
	if (address.interfaceNum != 0) fs << "interfaceNum" << (uint16_t)address.interfaceNum;
	if (!address.serialString.empty()) fs << "serialString" << address.serialString;
	fs << "}";
}

static void ReadCameraData(FileStorage& fs) {
	FileNode cameraRoot = fs["CameraData"];
	cameraData = new vector<CameraData>(cameraRoot.size());
	cout << "Loading " << cameraRoot.size() << " cameras from file" << endl;
	for (int i = 0; i < cameraRoot.size(); i++)
	{
		FileNode cd = cameraRoot[i];
		CameraData data;

		data.cameraName = cd["name"].string();

		FileNode prefabName = cd["prefab"];
		if (prefabName.isString()) data.prefabName = prefabName.string();

		ReadAddress(cd["address"], &data.address);


		cameraData->at(i) = data;
	}
}
static void WriteCameraData(FileStorage& fs) {
	if (cameraData->empty()) return;
	fs << "CameraData" << "[";
	for (int i = 0; i < cameraData->size(); i++)
	{
		CameraData& data = cameraData->at(i);
		fs << "{";
		fs << "name" << data.cameraName;
		fs << "prefab" << data.prefabName;
		fs << "address";
		WriteAddress(fs, data.address);
		fs << "}";
	}
	fs << "]";
}

static void ReadCameraPrefabs(FileStorage& fs) {
	FileNode prefabRoot = fs["Prefabs"];
	cameraPrefabs = new vector<CameraPrefab>(prefabRoot.size());
	cout << "Loading " << prefabRoot.size() << " prefabs from file" << endl;
	for (int i = 0; i < prefabRoot.size(); i++)
	{
		FileNode cd = prefabRoot[i];
		CameraPrefab data;

		data.prefabName = cd["name"].string();

		ReadAddress(cd["address"], &data.address);


		cameraPrefabs->at(i) = data;
	}
}
static void WriteCameraPrefabs(FileStorage& fs) {
	if (cameraPrefabs->empty()) return;
	fs << "Prefabs" << "[";
	for (int i = 0; i < cameraPrefabs->size(); i++)
	{
		CameraPrefab& data = cameraPrefabs->at(i);
		fs << "{";
		fs << "name" << data.prefabName;
		fs << "address";
		WriteAddress(fs, data.address);
		fs << "}";
	}
	fs << "]";
}

bool LoadCameraData(string path) {

	FileStorage fs;
	if (!fs.open(path, false)) {

		cameraData = new vector<CameraData>();
		cameraPrefabs = new vector<CameraPrefab>();
		return false;
	}

	ReadCameraData(fs);
	ReadCameraPrefabs(fs);

	return true;
}
bool SaveCameraData(string path) {
	FileStorage fs;
	if (!fs.open(path, FileStorage::WRITE)) return false;

	WriteCameraData(fs);
	WriteCameraPrefabs(fs);

	fs.release();
	return true;
}

USBDeviceAddress GetAddressFromDevicePath(string path) {
	USBDeviceAddress addr;
	vector<string> split;
	StringSplit(path, "#", &split);

	string str = split.at(1);
	addr.serialString = split.at(2);

	split.clear();
	StringSplit(str, "&", &split);

	addr.VendorID = stoul(split.at(0).substr(4, 4), nullptr, 16);
	addr.ProductID = stoul(split.at(1).substr(4, 4), nullptr, 16);

	if (split.size() == 3) addr.interfaceNum = stoul(split.at(2).substr(3, 2), nullptr, 16);

	return addr;
}
CameraData* FindCameraData(USBDeviceAddress &address) {
	if (cameraData != nullptr) {
		for (int i = 0; i < cameraData->size(); i++)
		{
			CameraData& data = cameraData->at(i);

			if (data.address.serialString == address.serialString) {
				return &cameraData->at(i);
			}
		}
	}
	return nullptr;
}

CameraPrefab* FindCameraPrefab(USBDeviceAddress& address) {
	if (cameraPrefabs != nullptr) {
		for (int i = 0; i < cameraPrefabs->size(); i++)
		{
			CameraPrefab* data = &cameraPrefabs->at(i);
			if (data->address.serialString == address.serialString) {
				return data;
			}
		}
	}
	return nullptr;
}

void RegisterCamera(CameraData data) {
	//do existance check?
	cameraData->push_back(data);
}
void RegisterCamera(CameraEnum* data, string prefabName) {
	return RegisterCamera(data, GetAddressFromDevicePath(data->devicePath), prefabName);
}
void RegisterCamera(CameraEnum* data, CameraPrefab* prefab) {
	return RegisterCamera(data, GetAddressFromDevicePath(data->devicePath), prefab);
}
void RegisterCamera(CameraEnum* data, USBDeviceAddress addr, string prefabName) {
	CameraPrefab* prefab = FindCameraPrefab(addr);
	if (prefab != 0) return RegisterCamera(data, addr, prefab);

	CameraData cam;
	cam.address = addr;
	cam.cameraName = data->description;
	return RegisterCamera(cam);
}
void RegisterCamera(CameraEnum* data, USBDeviceAddress addr, CameraPrefab* prefab) {
	CameraData cam;
	cam.address = addr;
	cam.cameraName = data->description;
	//apply prefab

	return RegisterCamera(cam);
}