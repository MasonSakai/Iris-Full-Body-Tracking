#include "IrisWebClient.h"
#include <iostream>
#include "util.h"
#include "IrisWebClient_keys.h"
using namespace IrisFBT;
using json = nlohmann::json;
using std::cout;
using std::endl;
using std::string;
using std::wstring;
using std::stringstream;
using std::wstringstream;

IrisWebClient::IrisWebClient(IrisWebServer* server, shared_ptr<WsServer::Connection> connection, intptr_t key) : server_(server), connection_(connection), socket_key_(key), display_name_(std::to_string(key)){
	cout << "on_open: " << display_name_ << endl;
	//connection.get()->send("{ \"type\": \"imgReq\" }");
}

IrisWebClient::~IrisWebClient() {
	cout << "on_close: " << display_name_ << endl;
}

void IrisWebClient::stop() {
	cout << "stop: " << display_name_ << endl;
	connection_.get()->send_close(1001, "Service closing");
}


void IrisWebClient::on_message(shared_ptr<WsServer::InMessage> in_message) {
	json json_message = json::parse(in_message.get()->string());
	IrisSocket_Key key = json_message["key"].get<IrisSocket_Key>();

	switch (key) {
	case IRISSOCKET_KEY_POSE:
	{
		json::array_t pose = json_message["pose"];


		break;
	}
	case IRISSOCKET_KEY_IMAGE:
	{
		//string data = json_message["data"].get<string>();


		break;
	}
	case IRISSOCKET_KEY_DECLARE:
	{
		camera_key_ = json_message["name"].get<string>();
		cout << "Declared " << display_name_ << " as " << camera_key_ << endl;
		display_name_ = camera_key_;

		break;
	}
	default:
		cout << "on_message: " << display_name_ << " (unhandled): " << json_message << endl;
		break;
	}
}
