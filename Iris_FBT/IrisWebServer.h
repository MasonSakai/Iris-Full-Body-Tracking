#pragma once
#include <nlohmann/json.hpp>
#include <sockpp/tcp_acceptor.h>
#include <httplib.h>
#include <mutex>
#include <wtypes.h>

#define IRIS_MAX_CLIENTS 32

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

		std::wstring path_driver;
		std::wstring path_config;
		nlohmann::json server_config;

		std::mutex server_thread_mutex;
		IrisServerState server_state;
		std::unique_ptr<httplib::Server> server_http;
		std::unique_ptr<sockpp::tcp_acceptor> server_socket;

		std::unique_ptr<IrisWebClient> clients[IRIS_MAX_CLIENTS];
	private:
		HANDLE server_socket_thread_handle_, server_http_thread_handle_;
		DWORD server_socket_thread_id_, server_http_thread_id_;

		FILE* file_log_;
	};

	extern IrisWebServer* web_server;
}

