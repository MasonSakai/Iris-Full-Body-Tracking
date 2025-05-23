#pragma once
#include "IrisWebServer.h"
#include <sockpp/tcp_socket.h>

namespace IrisFBT {

	class IrisWebClient
	{
	public:
		IrisWebClient(IrisWebServer* server, sockpp::tcp_socket client_socket, int client_index);
		~IrisWebClient();
		void Close();

		IrisWebServer* server;

		bool close;
		std::mutex client_thread_mutex;
		sockpp::tcp_socket client_socket;
		int client_index;

	private:
		HANDLE client_thread_handle_;
		DWORD client_thread_id_;
	};

}