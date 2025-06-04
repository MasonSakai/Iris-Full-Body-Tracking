#pragma once
#include "IrisWebClient.h"
#include <httplib.h>
#include <mutex>
#include <wtypes.h>
#include <unordered_map>
using std::unique_ptr;

namespace IrisFBT {

	class IrisWebServer
	{
	public:
		IrisWebServer();
		~IrisWebServer();

		void ServerSocketCallback(unsigned short port);

		std::wstring path_driver;
		std::wstring path_config;
		nlohmann::json server_config;

		unique_ptr<httplib::Server> server_http;
		unique_ptr<WsServer> server_socket;

	private:
		HANDLE server_http_thread_handle_, server_socket_thread_handle_;
		DWORD server_http_thread_id_, server_socket_thread_id_;

		FILE* file_log_;

		std::unordered_map<intptr_t, unique_ptr<IrisWebClient>> clients;
	};

	extern unique_ptr<IrisWebServer> web_server;
}

