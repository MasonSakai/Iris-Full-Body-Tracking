#include "IrisWebServer.h"
#include "IrisWebClient.h"
#include "openvr_driver.h"
#include <thread>
#include <fstream>
#include <iostream>
#include <windows.h>
#include <sstream>
#include <codecvt>
#include <io.h>
#include <winsock2.h>
#include <ws2tcpip.h>
#pragma comment(lib, "Ws2_32.lib")
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

	ZeroMemory(clients, sizeof(clients));

	server_state = IrisServer_PreInit;
	server_socket = INVALID_SOCKET;

	server_thread_handle_ = CreateThread(
		NULL,
		0,
		ServerThreadFunction,
		this,
		0,
		&server_thread_id_
	);


	while (true) {
		server_thread_mutex.lock();
		if (server_state == IrisServer_Error) break;
		else if (server_state == IrisServer_Ready) {
			server_state = IrisServer_Start;
			break;
		}
		server_thread_mutex.unlock();
	}
	server_thread_mutex.unlock();
}

IrisWebServer::~IrisWebServer() { Close(); }
void IrisWebServer::Close() {
	server_thread_mutex.lock();
	server_state = IrisServer_Closing;
	closesocket(server_socket);
	server_thread_mutex.unlock();

	WaitForSingleObject(server_thread_handle_, INFINITE);

	CloseHandle(server_thread_handle_);
}

DWORD WINAPI ServerThreadFunction(LPVOID lpParam) {
	IrisWebServer* server = (IrisWebServer*)lpParam;
	FILE* file_log = nullptr;

	server->server_thread_mutex.lock();
	server->server_state = IrisServer_Starting;
	server->server_thread_mutex.unlock();

	{
		std::wstring pathstr = server->path_driver + L"/logs";
		CreateDirectory(pathstr.c_str(), NULL);
		pathstr += L"/serverlog.txt";
		errno_t err = _wfreopen_s(&file_log, pathstr.c_str(), L"w", stdout);
		if (err != 0) {
			vr::VRDriverLog()->Log("Server Thread: Failed to redirect stdout for log");
		}
	}

	std::cout << "Server thread started, starting server..." << std::endl;
	
	{
		struct addrinfo* result = NULL, * ptr = NULL, hints;

		ZeroMemory(&hints, sizeof(hints));
		hints.ai_family = AF_INET;
		hints.ai_socktype = SOCK_STREAM;
		hints.ai_protocol = IPPROTO_TCP;
		hints.ai_flags = AI_PASSIVE;

		std::string port;
		if (server->server_config["port"].is_string()) {
			port = server->server_config["port"].get<std::string>();
		}
		else {
			port = "2674";
		}

		auto iResult = getaddrinfo(NULL, port.c_str(), &hints, &result);
		if (iResult != 0) {
			if (file_log == nullptr) {
				std::string str = "Server Thread: Failed to get address: ";
				str += iResult;
				vr::VRDriverLog()->Log(str.c_str());
			}
			else {
				std::cout << "Failed to get address: " << iResult << std::endl;
			}
			WSACleanup();
			if (file_log != nullptr) {
				fflush(stdout);
				fclose(file_log);
			}
			server->server_thread_mutex.lock();
			server->server_state = IrisServer_Error;
			server->server_thread_mutex.unlock();
			return 1;
		}
		std::cout << "Got address..." << std::endl;

		server->server_socket = socket(result->ai_family, result->ai_socktype, result->ai_protocol);
		if (server->server_socket == INVALID_SOCKET) {
			if (file_log == nullptr) {
				vr::VRDriverLog()->Log("Server Thread: Failed to open socket");
			}
			else {
				std::cout << "Failed to open socket" << std::endl;
			}
			freeaddrinfo(result);
			WSACleanup();
			if (file_log != nullptr) {
				fflush(stdout);
				fclose(file_log);
			}
			server->server_thread_mutex.lock();
			server->server_state = IrisServer_Error;
			server->server_thread_mutex.unlock();
			return 1;
		}
		std::cout << "Got socket..." << std::endl;

		if (bind(server->server_socket, result->ai_addr, (int)result->ai_addrlen) == SOCKET_ERROR) {
			if (file_log == nullptr) {
				std::string str = "Server Thread: Failed to bind socket: ";
				str += WSAGetLastError();
				vr::VRDriverLog()->Log(str.c_str());
			}
			else {
				std::cout << "Failed to bind socket: " << WSAGetLastError() << std::endl;
			}
			freeaddrinfo(result);
			closesocket(server->server_socket);
			WSACleanup();
			if (file_log != nullptr) {
				fflush(stdout);
				fclose(file_log);
			}
			server->server_thread_mutex.lock();
			server->server_state = IrisServer_Error;
			server->server_thread_mutex.unlock();
			return 1;
		}
		std::cout << "Bound socket..." << std::endl;

		freeaddrinfo(result);

		server->server_thread_mutex.lock();
		server->server_state = IrisServer_Ready;
		server->server_thread_mutex.unlock();
		std::cout << "Server is ready!" << std::endl;

		while (true) {
			server->server_thread_mutex.lock();
			if (server->server_state == IrisServer_Start) break;
			else if (server->server_state == IrisServer_Closing) {
				server->server_thread_mutex.unlock();
				std::cout << "Preemptively closing server" << std::endl;

				closesocket(server->server_socket);
				WSACleanup();
				if (file_log != nullptr) {
					fflush(stdout);
					fclose(file_log);
				}
				server->server_thread_mutex.lock();
				server->server_state = IrisServer_Closed;
				server->server_thread_mutex.unlock();
				return 0;
			}
			server->server_thread_mutex.unlock();
		}
		server->server_thread_mutex.unlock();
		std::cout << "Got go command..." << std::endl;

		if (listen(server->server_socket, SOMAXCONN) == SOCKET_ERROR) {
			if (file_log == nullptr) {
				std::string str = "Server Thread: Failed to listen: ";
				str += WSAGetLastError();
				vr::VRDriverLog()->Log(str.c_str());
			}
			else {
				std::cout << "Failed to listen: " << WSAGetLastError() << std::endl;
			}
			closesocket(server->server_socket);
			WSACleanup();
			if (file_log != nullptr) {
				fflush(stdout);
				fclose(file_log);
			}
			server->server_thread_mutex.lock();
			server->server_state = IrisServer_Error;
			server->server_thread_mutex.unlock();
			return 1;
		}
	}
	std::cout << "Socket is listening..." << std::endl;

	server->server_thread_mutex.lock();
	server->server_state = IrisServer_Online;
	server->server_thread_mutex.unlock();

	std::cout << "Server is online!" << std::endl;

	bool socketClosed = false;

	SOCKET client_socket;
	server->server_thread_mutex.lock();
	while (server->server_state == IrisServer_Online) {
		server->server_thread_mutex.unlock();

		client_socket = accept(server->server_socket, NULL, NULL);
		if (client_socket == INVALID_SOCKET) {
			std::cout << "Failed to accept: " << WSAGetLastError() << std::endl;

			server->server_thread_mutex.lock();
			{
				if (server->server_state == IrisServer_Closing) {
					goto exit;
				}

				if (WSAGetLastError() == WSAENOTSOCK) {
					socketClosed = true;
					goto exit;
				}
			}
			server->server_thread_mutex.unlock();
			continue;
		exit:
			server->server_state = IrisServer_Closing;
			break;
		}

		int clientIndex = IRIS_MAX_CLIENTS;

		while (clientIndex == IRIS_MAX_CLIENTS) {
			server->server_thread_mutex.lock();
			if (server->server_state == IrisServer_Closing) {
				closesocket(client_socket);
				goto exit;
			}

			for (clientIndex = 0; clientIndex < IRIS_MAX_CLIENTS; clientIndex++) {
				if (server->clients[clientIndex] == nullptr) break;
			}
			server->server_thread_mutex.unlock();
		}

		std::cout << "Binding client to: " << clientIndex << std::endl;
		server->clients[clientIndex] = std::make_unique<IrisWebClient>(server, client_socket, clientIndex);

		server->server_thread_mutex.lock();
	}
	server->server_thread_mutex.unlock();

	for (int i = 0; i < IRIS_MAX_CLIENTS; i++) {
		if (server->clients[i] != nullptr) {
			server->clients[i].get()->Close();
			server->clients[i] = nullptr;
		}
	}
	if (!socketClosed) closesocket(server->server_socket);
	server->server_thread_mutex.lock();
	server->server_socket = INVALID_SOCKET;
	server->server_thread_mutex.unlock();

	WSACleanup();

	if (file_log != nullptr) {
		fflush(stdout);
		fclose(file_log);
	}

	server->server_thread_mutex.lock();
	server->server_state = IrisServer_Closed;
	server->server_thread_mutex.unlock();

	return 0;
}