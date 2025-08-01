#include "IrisSocketClient.h"
#include "ClientConfig.h"
#include <openvr_driver.h>
#include "util.h"
using namespace IrisFBT;

namespace IrisFBT {
    std::unique_ptr<IrisSocketClient> iris_client = nullptr;
}

IrisSocketClient::IrisSocketClient(DeviceProvider* provider)
{
    this->provider = provider;

    json& config = ClientConfig::Get();
    if (!config.contains("core_url")) {
        config["core_url"] = "http://localhost:2674";
    }
    string url = config["core_url"].get<std::string>();
    vr::VRDriverLog()->Log(("Server URL: " + url).c_str());

    client.set_open_listener([&]()
        {
            if (hasConnected) {
                vr::VRDriverLog()->Log("Reconnected to server");
                return;
            }
            hasConnected = true;
            vr::VRDriverLog()->Log("Connected to server");

            this->provider->InitTrackers();

            client.socket("/sioModule")->on("pose", std::bind(&IrisSocketClient::on_pose, this, std::placeholders::_1));
        });
    client.set_close_listener([&](sio::client::close_reason const& reason)
        {
            vr::VRDriverLog()->Log("Disconnected from server");
        });

    client.set_fail_listener([&]()
        {
            vr::VRDriverLog()->Log("Failed to connect to server");
        });

    client.connect(url);
}

IrisSocketClient::~IrisSocketClient()
{
    client.sync_close();
}

void IrisSocketClient::on_pose(sio::event& event)
{
    json data = messageToJson(event.get_message());
    //vr::VRDriverLog()->Log(("Got message: " + data.dump()).c_str());

    if (!data.is_null()) {
        provider->mtx_deviceRegister.lock();
        for (uint8_t i = 0; i < IrisTracker_Count; i++) {
            IrisTrackerDevice* tracker = provider->GetDevice(i);
            if (tracker != nullptr) {
                const string& ident = IrisTracker_IndexMap.at(i);
                if (data.contains(ident)) {
                    tracker->UpdatePose(data[ident].get<vector<vector<double>>>());
                }
                else {
                    tracker->UpdatePoseEmpty();
                }
            }
        }
        provider->mtx_deviceRegister.unlock();

        IrisCalibrator::on_pose(data);
    }
}
