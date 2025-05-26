#include "IrisWebClient.h"
#include <thread>
#include <windows.h>
#include <iostream>
#include <string>
#include <sstream>
#include <vector>
#include "PathUtil.h"
using namespace IrisFBT;
using json = nlohmann::json;
template <typename T>
using shared_ptr = std::shared_ptr<T>;
using WsServer = SimpleWeb::SocketServer<SimpleWeb::WS>;
using std::cout;
using std::endl;
using std::string;
using std::wstring;
using std::stringstream;
using std::wstringstream;

IrisWebClient::IrisWebClient(IrisWebServer* server, shared_ptr<WsServer::Connection> connection, intptr_t key) : server_(server), connection_(connection), key_(key) {
	cout << "on_open: " << key_ << endl;
}

IrisWebClient::~IrisWebClient() {
	cout << "on_close: " << key_ << endl;
}

void IrisWebClient::stop() {
	cout << "stop: " << key_ << endl;
	connection_.get()->send_close(1001, "Service closing");
}


void IrisWebClient::on_message(shared_ptr<WsServer::InMessage> in_message) {
	json data = json::parse(in_message.get()->string());
	string type = data["type"].get<string>();

	if (type == "pose") {
		json::array_t pose = data["pose"];
		
	}
	else {
		cout << "on_message: " << key_ << " (unhandled): " << data << endl;
	}
}

std::vector<std::string> split(const std::string& text, char delimiter) {
	std::vector<std::string> result;
	std::string::size_type start = 0;
	std::string::size_type end = text.find(delimiter);

	while (end != std::string::npos) {
		result.push_back(text.substr(start, end - start));
		start = end + 1;
		end = text.find(delimiter, start);
	}
	result.push_back(text.substr(start));
	return result;
}