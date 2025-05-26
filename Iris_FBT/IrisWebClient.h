#pragma once
#include "IrisWebServer.h"
using WsServer = SimpleWeb::SocketServer<SimpleWeb::WS>;

namespace IrisFBT {

	class IrisWebClient
	{
	public:
		IrisWebClient(IrisWebServer* server, std::shared_ptr<WsServer::Connection> connection, intptr_t key);
		~IrisWebClient();

		void on_message(std::shared_ptr<WsServer::InMessage> in_message);

		void stop();

	private:

		intptr_t key_;

		IrisWebServer* server_;
		std::shared_ptr<WsServer::Connection> connection_;

	};

}