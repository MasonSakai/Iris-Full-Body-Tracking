#pragma once
#include "IrisWebServer.h"
#include <string>
using std::string;

namespace IrisFBT {

	class IrisWebClient
	{
	public:
		IrisWebClient(IrisWebServer* server, shared_ptr<WsServer::Connection> connection, intptr_t key);
		~IrisWebClient();

		void on_message(shared_ptr<WsServer::InMessage> in_message);

		void stop();

	private:

		intptr_t socket_key_;
		string camera_key_, display_name_;

		IrisWebServer* server_;
		shared_ptr<WsServer::Connection> connection_;

	};

}