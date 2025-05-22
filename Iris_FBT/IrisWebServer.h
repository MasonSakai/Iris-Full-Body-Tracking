#pragma once
#include <WinSock2.h>
#include <WS2tcpip.h>
#include <nlohmann/json.hpp>
#include <mutex>

namespace IrisFBT {

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
		bool run;
		SOCKET svr;
	private:
		HANDLE server_thread_handle_;
		DWORD server_thread_id_;
	};

	extern IrisWebServer* web_server;
}

