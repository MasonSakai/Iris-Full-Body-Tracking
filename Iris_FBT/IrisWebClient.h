#pragma once
#include "IrisWebServer.h"

namespace IrisFBT {

	class IrisWebClient
	{
	public:
		IrisWebClient(IrisWebServer* server, SOCKET client_socket, int client_index);
		~IrisWebClient();
		void Close();

		IrisWebServer* server;

		bool close;
		std::mutex client_thread_mutex;
		SOCKET client_socket;
		int client_index;

	private:
		HANDLE client_thread_handle_;
		DWORD client_thread_id_;
	};

}