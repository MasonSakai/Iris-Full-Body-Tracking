#include "IrisWebServer.h"
#include "IrisWebClient.h"
#include "openvr_driver.h"
#include <thread>
#include <fstream>
#include <iostream>
#include <windows.h>
#include <sstream>
#include <io.h>
#include <sockpp/tcp_socket.h>
#include "PathUtil.h"
using namespace IrisFBT;
using json = nlohmann::json;

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

	ZeroMemory(clients, sizeof(clients));

	server_state = IrisServer_PreInit;
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

}

IrisWebServer::~IrisWebServer() { Close(); }
void IrisWebServer::Close() {
	server_thread_mutex.lock();
	server_state = IrisServer_Closing;
	server_socket.get()->close();
	server_thread_mutex.unlock();

	server_http.get()->stop();
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

	for (int i = 0; i < IRIS_MAX_CLIENTS; i++) {
		if (clients[i] != nullptr) {
			clients[i].get()->Close();
			clients[i] = nullptr;
		}
	}

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

	int port = 2674;
	if (server->server_config["http_port"].is_number_unsigned()) {
		port = server->server_config["http_port"].get<int>();
	}
	else server->server_config["http_port"] = port;

	server->server_http = std::make_unique<httplib::Server>();

	server->server_http.get()->set_logger([](const httplib::Request& req, const httplib::Response& res) {
		std::cout << "HTTP: " << req.body << " : " << res.body << std::endl;
	});

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

	return 0;
}


DWORD WINAPI ServerSocketThreadFunction(LPVOID lpParam) {
	IrisWebServer* server = (IrisWebServer*)lpParam;

	server->server_thread_mutex.lock();
	server->server_state = IrisServer_Starting;
	server->server_thread_mutex.unlock();

	std::cout << "Server thread started, starting server..." << std::endl;
	
	sockpp::initialize();
	
	{
		in_port_t port = 2673;
		if (server->server_config["socket_port"].is_number_unsigned()) {
			port = server->server_config["socket_port"].get<in_port_t>();
		}
		else server->server_config["socket_port"] = port;

		int queueSize = 4;
		try {
			if (server->server_config.at("socket_queueSize").is_number_integer()) {
				queueSize = server->server_config["socket_queueSize"].get<int>();
			}
		}
		catch (...) {}

		server->server_socket = std::make_unique<sockpp::tcp_acceptor>(port, queueSize);

		if (!*(server->server_socket.get())) {
			std::cout << "Failed to open socket: " << server->server_socket.get()->last_error_str() << std::endl;
			server->server_thread_mutex.lock();
			server->server_state = IrisServer_Error;
			server->server_thread_mutex.unlock();
			return 1;
		}

		std::cout << "Socket is listening on port " << port << "..." << std::endl;
	}

	server->server_thread_mutex.lock();
	server->server_state = IrisServer_Online;
	server->server_thread_mutex.unlock();

	std::cout << "Server is online!" << std::endl;

	server->server_thread_mutex.lock();
	while (server->server_state == IrisServer_Online) {
		server->server_thread_mutex.unlock();

		sockpp::tcp_socket client_socket = server->server_socket.get()->accept();
		if (!client_socket) {
			std::cout << "Failed to accept: " << server->server_socket.get()->last_error_str() << std::endl;

			server->server_thread_mutex.lock();
			if (!server->server_socket.get()->is_open()) {
				server->server_state = IrisServer_Closing;
				break;
			}
		}
		else {
			std::cout << "Got client! Finding index..." << std::endl;

			int clientIndex = IRIS_MAX_CLIENTS;

			while (clientIndex == IRIS_MAX_CLIENTS) {
				server->server_thread_mutex.lock();
				if (server->server_state != IrisServer_Online) {
					client_socket.close();
					goto exit;
				}

				for (clientIndex = 0; clientIndex < IRIS_MAX_CLIENTS; clientIndex++) {
					if (server->clients[clientIndex] == nullptr)
						break;
				}
				server->server_thread_mutex.unlock();
			}

			std::cout << "Binding client to: " << clientIndex << std::endl;
			server->clients[clientIndex] = std::make_unique<IrisWebClient>(server, std::move(client_socket), clientIndex);

			server->server_thread_mutex.lock();
		}
	}
exit:
	server->server_thread_mutex.unlock();

	server->server_thread_mutex.lock();
	if (server->server_socket.get()->is_open()) server->server_socket.get()->close();
	delete server->server_socket.release();
	server->server_socket = nullptr;
	server->server_state = IrisServer_Closed;
	server->server_thread_mutex.unlock();

	return 0;
}