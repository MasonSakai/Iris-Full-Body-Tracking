#pragma once
#include <nlohmann/json.hpp>
#include <server_ws.hpp>
#include <httplib.h>
#include <mutex>
#include <wtypes.h>
#include <unordered_map>
using WsServer = SimpleWeb::SocketServer<SimpleWeb::WS>;

namespace IrisFBT {

	typedef enum {
		IrisServer_PreInit,
		IrisServer_Starting,
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

		void ServerSocketCallback(unsigned short port);

		std::wstring path_driver;
		std::wstring path_config;
		nlohmann::json server_config;

		std::unique_ptr<httplib::Server> server_http;
		std::unique_ptr<WsServer> server_socket;

	private:
		HANDLE server_http_thread_handle_, server_socket_thread_handle_;
		DWORD server_http_thread_id_, server_socket_thread_id_;

		FILE* file_log_;

		std::unordered_map<intptr_t, std::unique_ptr<IrisWebClient>> clients;
	};

	extern IrisWebServer* web_server;
}

