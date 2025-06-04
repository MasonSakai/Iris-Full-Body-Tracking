#pragma once
#include <server_ws.hpp>
#include <string>
#include <nlohmann/json.hpp>
using std::shared_ptr;
using std::string;
using WsServer = SimpleWeb::SocketServer<SimpleWeb::WS>;
using json = nlohmann::json;

namespace IrisFBT {

	class IrisWebClient
	{
	public:
		IrisWebClient(shared_ptr<WsServer::Connection> connection, intptr_t key);
		~IrisWebClient();

		void on_message(shared_ptr<WsServer::InMessage> in_message);

		void stop();

	private:

		intptr_t socket_key_;
		string camera_key_, display_name_;

		shared_ptr<WsServer::Connection> connection_;

		json config_;

	};

}