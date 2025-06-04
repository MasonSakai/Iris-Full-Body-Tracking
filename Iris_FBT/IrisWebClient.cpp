#include "IrisWebClient.h"
#include <iostream>
#include "util.h"
#include "IrisWebClient_keys.h"
#include "CameraConfig.h"
using namespace IrisFBT;
using json = nlohmann::json;
using std::cout;
using std::endl;
using std::string;
using std::wstring;
using std::stringstream;
using std::wstringstream;

IrisWebClient::IrisWebClient(shared_ptr<WsServer::Connection> connection, intptr_t key) : connection_(connection), socket_key_(key), display_name_(std::to_string(key)) {
	cout << "on_open: " << display_name_ << endl;
	//connection->send("{ \"key\": \"imgReq\" }");
}

IrisWebClient::~IrisWebClient() {
	cout << "on_close: " << display_name_ << endl;
}

void IrisWebClient::stop() {
	cout << "stop: " << display_name_ << endl;
	connection_->send_close(1001, "Service closing");
}


void IrisWebClient::on_message(shared_ptr<WsServer::InMessage> in_message) {
	json json_message = json::parse(in_message->string());
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

		if (CameraConfig::Find(config_, display_name_)) {
			cout << display_name_ << ": Could not find config..." << endl;
			json j = { { "key", IRISSOCKET_KEY_CONFIG_NOTFOUND } };
			connection_->send(j.dump());
		}
		else {
			string name = config_["name"].get<string>();
			cout << "Got name of " << display_name_ << " as " << name << endl;
			display_name_ = name;
		}

		break;
	}
	case IRISSOCKET_KEY_CONFIG_POST:
	{
		if (config_.is_null()) {
			config_ = CameraConfig::Get(display_name_);
		}

		if (json_message.contains("name")) {
			string name = json_message["name"].get<string>();
			if (name != display_name_) {
				cout << "Renaming " << display_name_ << " to " << name << endl;
				if (!CameraConfig::Rename(display_name_, name)) {
					cout << "Error renaming " << display_name_ << " to " << name << endl;
					
				}
				else {
					cout << (config_ == CameraConfig::Get(name)) << endl;
					display_name_ = name;
				}
			}
		}

		json_message.erase("key");
		config_.update(json_message);
		CameraConfig::Get(display_name_) = config_;

		break;
	}
	default:
		cout << "on_message: " << display_name_ << " (unhandled): " << json_message << endl;
		break;
	}
}
