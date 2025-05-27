#include "IrisWebServer.h"
#include "IrisWebClient.h"
#include "openvr_driver.h"
#include <thread>
#include <fstream>
#include <iostream>
#include <windows.h>
#include <sstream>
#include <io.h>
#include "util.h"
using namespace IrisFBT;
using json = nlohmann::json;
using std::cout;
using std::endl;
using std::string;

DWORD WINAPI ServerHttpThreadFunction(LPVOID lpParam);
DWORD WINAPI ServerSocketThreadFunction(LPVOID lpParam);

namespace IrisFBT {
	IrisWebServer* web_server = nullptr;
}

IrisWebServer::IrisWebServer() {

	web_server = this;

	path_driver = getDriverPath();
	path_config = getAppdata();
	std::wstring configPath = path_config + L"serverConfig.json";

	{
		std::wstringstream pathString;
		pathString << L"Driver Path: " << path_driver;
		pathString << std::endl;
		pathString << L"Config Path: " << path_config;
		std::wstring wstr = pathString.str();

		size_t len = (wcslen(wstr.c_str()) + 1) * sizeof(wchar_t);
		char* buffer = new char[len];
		size_t convertedSize;
		wcstombs_s(&convertedSize, buffer, len, wstr.c_str(), len);
		vr::VRDriverLog()->Log(buffer);
		delete[] buffer;
	}

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
	else if (CreateDirectoryW(path_config.c_str(), NULL)) {
		std::ofstream fw(configPath);
		fw << "{}";
		fw.close();
	}

	server_socket = nullptr;
	file_log_ = nullptr;

	{
		std::wstring pathstr = path_driver + L"/logs";
		CreateDirectoryW(pathstr.c_str(), NULL);
		pathstr += L"/serverlog.txt";
		errno_t err = _wfreopen_s(&file_log_, pathstr.c_str(), L"w", stdout);
		if (err != 0) {
			vr::VRDriverLog()->Log("Server Thread: Failed to redirect stdout for log");
		}
	}

	server_http_thread_handle_ = CreateThread(
		NULL,
		0,
		ServerHttpThreadFunction,
		this,
		0,
		&server_http_thread_id_
	);

	server_socket_thread_handle_ = CreateThread(
		NULL,
		0,
		ServerSocketThreadFunction,
		this,
		0,
		&server_socket_thread_id_
	);
	

	std::cout << "Setup complete!" << std::endl;
}

IrisWebServer::~IrisWebServer() { Close(); }
void IrisWebServer::Close() {
	server_http.get()->stop();
	server_socket.get()->stop_accept();
	for (auto& pair : clients) {
		pair.second.get()->stop();
	}

	DWORD result = WaitForSingleObject(server_http_thread_handle_, INFINITE);
	if (result == WAIT_OBJECT_0)
		std::cout << "Http thread finished execution." << std::endl;
	else std::cout << "Http thread: wait failed or timed out: " << result << std::endl;
	CloseHandle(server_http_thread_handle_);

	result = WaitForSingleObject(server_socket_thread_handle_, INFINITE);
	if (result == WAIT_OBJECT_0)
		std::cout << "Socket thread finished execution." << std::endl;
	else std::cout << "Socket thread: wait failed or timed out: " << result << std::endl;
	CloseHandle(server_socket_thread_handle_);

	if (file_log_ != nullptr) {
		fflush(stdout);
		fclose(file_log_);
	}


	std::wstring configPath = path_config + L"serverConfig.json";
	std::ofstream f(configPath.c_str());
	f << std::setw(4) << server_config;
	f.close();
}

DWORD WINAPI ServerHttpThreadFunction(LPVOID lpParam) {
	IrisWebServer* server = (IrisWebServer*)lpParam;
	cout << "HTTP server thread start" << endl;

	int port = 2674;
	if (server->server_config["http_port"].is_number_unsigned()) {
		port = server->server_config["http_port"].get<int>();
	}
	else server->server_config["http_port"] = port;

	server->server_http = std::make_unique<httplib::Server>();

	std::wstring path = server->path_driver + L"/dist";
	size_t len = (wcslen(path.c_str()) + 1) * sizeof(wchar_t);
	char* buffer = new char[len];
	size_t convertedSize;
	wcstombs_s(&convertedSize, buffer, len, path.c_str(), len);
	auto ret = server->server_http.get()->set_mount_point("/", buffer);

	if (!ret) {
		vr::VRDriverLog()->Log("We don't have our website files!");
		return 1;
	}

	if (!server->server_http.get()->listen("localhost", port)) {
		vr::VRDriverLog()->Log("Failed to start http server!");
		return 1;
	}
	else vr::VRDriverLog()->Log("Started http server!");

	cout << "HTTP server thread stop" << endl;
	return 0;
}

DWORD WINAPI ServerSocketThreadFunction(LPVOID lpParam) {
	IrisWebServer* server = (IrisWebServer*)lpParam;
	cout << "Socket server thread start" << endl;

	int port = 2673;
	if (server->server_config["socket_port"].is_number_unsigned()) {
		port = server->server_config["socket_port"].get<int>();
	}
	else server->server_config["socket_port"] = port;

	server->server_socket = std::make_unique<WsServer>();
	auto socket = server->server_socket.get();
	socket->config.port = port;

	try {
		if (server->server_config.at("socket_port").is_number_unsigned()) {
			socket->config.thread_pool_size = server->server_config["socket_port"].get<size_t>();
		}
	}
	catch (...) {}

	socket->start([server](unsigned short port) { server->ServerSocketCallback(port); });

	cout << "Socket server thread stop" << endl;
	return 0;
}

void IrisWebServer::ServerSocketCallback(unsigned short port) {
	std::cout << "Socket server starting on port " << port << std::endl;

	auto server = server_socket.get();

	auto& pose = server->endpoint["^/?$"];


	pose.on_open = [this](shared_ptr<WsServer::Connection> connection) {
		intptr_t key = reinterpret_cast<intptr_t>(connection.get());
		clients[key] = std::make_unique<IrisWebClient>(this, connection, key);
	};

	// See RFC 6455 7.4.1. for status codes
	pose.on_close = [this](shared_ptr<WsServer::Connection> connection, int status, const std::string& reason) {
		intptr_t key = reinterpret_cast<intptr_t>(connection.get());
		clients.erase(key);
	};


	pose.on_message = [this](shared_ptr<WsServer::Connection> connection, shared_ptr<WsServer::InMessage> in_message) {
		intptr_t key = reinterpret_cast<intptr_t>(connection.get());
		clients[key].get()->on_message(in_message);
	};

	std::cout << "Socket server started!" << std::endl;
}