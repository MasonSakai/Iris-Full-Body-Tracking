#pragma once
#include "IrisWebServer.h"
using WsServer = SimpleWeb::SocketServer<SimpleWeb::WS>;

namespace IrisFBT {

	class IrisWebClient
	{
	public:
		IrisWebClient(IrisWebServer* server, int client_index);
		~IrisWebClient();

		void Close();

		IrisWebServer* server;

	private:

	};

}