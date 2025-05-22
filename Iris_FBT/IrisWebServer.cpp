#include "IrisWebServer.h"
#include "openvr_driver.h"
#include <thread>
#include <fstream>
#include <iostream>
#include <windows.h>
#include <sstream>
#include <codecvt>
#include <io.h>
#include "PathUtil.h"
using namespace IrisFBT;
using json = nlohmann::json;

DWORD WINAPI ServerThreadFunction(LPVOID lpParam);

namespace IrisFBT {
	IrisWebServer* web_server = nullptr;
}

IrisWebServer::IrisWebServer() {

	web_server = this;

	path_driver = getDriverPath();
	path_config = getAppdata();
	std::wstring configPath = path_config + L"serverConfig.json";

	std::wstring_convert<std::codecvt_utf8<wchar_t>> converter;
	std::wstringstream pathString;
	pathString << L"Driver Path: " << path_driver;
	pathString << std::endl;
	pathString << L"Config Path: " << path_config;
	vr::VRDriverLog()->Log(converter.to_bytes(pathString.str()).c_str());

	std::ifstream f(configPath.c_str());

	if (f.is_open()) {
		try {
			server_config = json::parse(f);
		}
		catch (std::exception e) {
			std::stringstream errorString;
			errorString << "Error reading config: " << e.what();
			vr::VRDriverLog()->Log(errorString.str().c_str());
		}
	}
	else if (CreateDirectory(path_config.c_str(), NULL)) {
		std::ofstream fw(configPath);
		fw << "Yoooo";
		fw.close();
	}


	run = true;

	server_thread_handle_ = CreateThread(
		NULL,
		0,
		ServerThreadFunction,
		this,
		0,
		&server_thread_id_
	);
}

IrisWebServer::~IrisWebServer() { Close(); }
void IrisWebServer::Close() {
	server_thread_mutex.lock();
	run = false;
	server_thread_mutex.unlock();

	WaitForSingleObject(server_thread_handle_, INFINITE);

	CloseHandle(server_thread_handle_);
}

DWORD WINAPI ServerThreadFunction(LPVOID lpParam) {
	IrisWebServer* server = (IrisWebServer*)lpParam;
	FILE* file_log = nullptr;

	{
		std::wstring pathstr = server->path_config + L"log.txt";
		const wchar_t* path = pathstr.c_str();
		errno_t err = _wfreopen_s(&file_log, path, L"w", stdout);
		if (err != 0) {
			vr::VRDriverLog()->Log("Server Thread: Failed to redirect stdout for log");
		}
	}

	std::cout << "Server thread starting..." << std::endl;
	


	server->server_thread_mutex.lock();
	while (server->run) {
		server->server_thread_mutex.unlock();



		std::cout << ".";
		std::this_thread::sleep_for(std::chrono::seconds(1));



		server->server_thread_mutex.lock();
	}

	if (file_log != nullptr) {
		fflush(stdout);
		fclose(file_log);
	}

	return 0;
}