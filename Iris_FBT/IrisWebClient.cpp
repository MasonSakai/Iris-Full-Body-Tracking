#include "IrisWebClient.h"
#include <winsock2.h>
#include <ws2tcpip.h>
#pragma comment(lib, "Ws2_32.lib")
#include <iostream>
#include "PathUtil.h"
using namespace IrisFBT;
using json = nlohmann::json;
using std::cout;
using std::endl;

DWORD WINAPI ClientThreadFunction(LPVOID lpParam);

IrisWebClient::IrisWebClient(IrisWebServer* server, SOCKET client_socket, int client_index) : server(server), client_socket(client_socket), client_index(client_index) {

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
	client_thread_mutex.lock();
	close = true;
	client_thread_mutex.unlock();

	WaitForSingleObject(client_thread_handle_, INFINITE);

	CloseHandle(client_thread_handle_);
}



DWORD WINAPI ClientThreadFunction(LPVOID lpParam) {
    IrisWebClient* client = static_cast<IrisWebClient*>(lpParam);


#define DEFAULT_BUFLEN 512

    char recvbuf[DEFAULT_BUFLEN];
    int iResult, iSendResult;
    int recvbuflen = DEFAULT_BUFLEN;

    std::string str;

    // Receive until the peer shuts down the connection
    do {

        iResult = recv(client->client_socket, recvbuf, recvbuflen, 0);
        if (iResult > 0) {
            printf("Bytes received: %d\n", iResult);

            str.append(recvbuf, recvbuflen);

            // Echo the buffer back to the sender
            iSendResult = send(client->client_socket, recvbuf, iResult, 0);
            if (iSendResult == SOCKET_ERROR) {
                printf("send failed: %d\n", WSAGetLastError());
                break;
            }
            printf("Bytes sent: %d\n", iSendResult);
        }
        else if (iResult == 0) {
            printf("Connection closing...\n");
            cout << str << endl;
            str.clear();
        }
        else {
            printf("recv failed: %d\n", WSAGetLastError());
            break;
        }

    } while (iResult > 0 && !client->close);

    closesocket(client->client_socket);

    client->server->server_thread_mutex.lock();
    client->server->clients[client->client_index].release();
    client->server->clients[client->client_index] = nullptr;
    client->server->server_thread_mutex.unlock();

	return 0;
}