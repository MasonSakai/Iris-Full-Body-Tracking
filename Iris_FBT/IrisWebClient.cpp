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
using std::cout;
using std::endl;
using std::string;
using std::wstring;
using std::stringstream;
using std::wstringstream;

DWORD WINAPI ClientThreadFunction(LPVOID lpParam);
std::vector<std::string> split(const std::string& text, char delimiter);

IrisWebClient::IrisWebClient(IrisWebServer* server, sockpp::tcp_socket client_socket, int client_index) : server(server), client_index(client_index) {

	this->client_socket = std::move(client_socket);

	close = false;

	client_thread_handle_ = CreateThread(
		NULL,
		0,
		ClientThreadFunction,
		this,
		0,
		&client_thread_id_
	);
}

IrisWebClient::~IrisWebClient() { Close(); }
void IrisWebClient::Close() {
	cout << "[" << client_index << "] Closing..." << endl;
	client_thread_mutex.lock();
	close = true;
	client_thread_mutex.unlock();

	client_socket.close();

	DWORD result = WaitForSingleObject(client_thread_handle_, INFINITE);
	if (result == WAIT_OBJECT_0) {
		std::cout << "[" << client_index << "] Thread finished execution." << std::endl;
	}
	else {
		std::cout << "[" << client_index << "] Wait failed or timed out: " << result << std::endl;
	}
	CloseHandle(client_thread_handle_);

	cout << "[" << client_index << "] Closed" << endl;
}

DWORD WINAPI ClientThreadFunction(LPVOID lpParam) {
    IrisWebClient* client = static_cast<IrisWebClient*>(lpParam);

	char buf[512];
	ssize_t n;

	stringstream requestStream;
	while (!client->close && (n = client->client_socket.read(buf, sizeof(buf))) > 0) {
		requestStream.write(buf, n);
	}
	string request = requestStream.str();
	cout << "[" << client->client_index << "] Got: \"" << request << "\"" << endl;

	cout << "[" << client->client_index << "] Connection closed from " << client->client_socket.peer_address() << endl;
	if (client->client_socket.is_open()) client->client_socket.close();

	cout << "[" << client->client_index << "] Awaiting closing..." << endl;
	/*client->server->server_thread_mutex.lock();
	cout << "[" << client->client_index << "] Got lock" << endl;
    client->server->clients[client->client_index].release();
	client->server->clients[client->client_index] = nullptr;
    client->server->server_thread_mutex.unlock();*/
	cout << "[" << client->client_index << "] We outa here!" << endl;

	return 0;
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