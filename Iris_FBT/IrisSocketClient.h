#pragma once
#include <sio_client.h>
#include "device_provider.h"

namespace IrisFBT {

	class IrisSocketClient
	{
	public:
		IrisSocketClient(DeviceProvider*);
		~IrisSocketClient();

		void on_pose(sio::event&);


	private:
		sio::client client;
		DeviceProvider* provider;
		bool hasConnected = false;
	};

	extern std::unique_ptr<IrisSocketClient> iris_client;
}