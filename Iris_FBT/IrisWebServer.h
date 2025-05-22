#pragma once
#include <WinSock2.h>
#include <WS2tcpip.h>
#include <nlohmann/json.hpp>
#include <mutex>

#define IRIS_MAX_CLIENTS 32

namespace IrisFBT {

	typedef enum {
		IrisServer_PreInit,
		IrisServer_Starting,
		IrisServer_Ready,
		IrisServer_Start,
		IrisServer_Online,
		IrisServer_Closing,
		IrisServer_Closed,
		IrisServer_Error
	} IrisServerState;

	class IrisWebClient;

	class IrisWebServer
	{
	public:
		IrisWebServer();
		~IrisWebServer();
		void Close();

		std::wstring path_driver;
		std::wstring path_config;
		nlohmann::json server_config;

		std::mutex server_thread_mutex;
		IrisServerState server_state;
		SOCKET server_socket;

		std::unique_ptr<IrisWebClient> clients[IRIS_MAX_CLIENTS];
	private:
		HANDLE server_thread_handle_;
		DWORD server_thread_id_;
	};

	extern IrisWebServer* web_server;
}

