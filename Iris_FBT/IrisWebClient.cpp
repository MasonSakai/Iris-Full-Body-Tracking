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
using WsServer = SimpleWeb::SocketServer<SimpleWeb::WS>;
using std::cout;
using std::endl;
using std::string;
using std::wstring;
using std::stringstream;
using std::wstringstream;

std::vector<std::string> split(const std::string& text, char delimiter);

IrisWebClient::IrisWebClient(IrisWebServer* server, int client_index) : server(server) {

}

IrisWebClient::~IrisWebClient() {

}

void IrisWebClient::Close() {

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