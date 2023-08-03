
//If you begin to have issues with boost libraries
//https://stackoverflow.com/questions/39363720/compiling-boost-with-msvc2015-with-stdclatest-or-c17-n4190

#include "DashboardWidget.h"
#include "VRDashboardOverlay.h"
#include "PoseTracker.h"
#include "websiteServer.h"
#include "vrUtil.h"
#include "CameraManager.h"
#include "OverlayManager.h"
#include "Config.h"

#include <QApplication>
#include <QDebug>
#include <Windows.h>
#include <iostream>
#include <thread>

std::thread MainThread;

void MainLoop() {
	active = true;

	uint8_t trackerStates[17];
	uint8_t i, j;
	bool completed;

	auto lastTime = std::chrono::high_resolution_clock::now();
	int numFramePresents = 0;
	float deltaTime;
	uint32_t currentFrame = 0;

	while (active) {
		if (vr::VRCompositor() != NULL) {
			vr::Compositor_FrameTiming t;
			t.m_nSize = sizeof(vr::Compositor_FrameTiming);
			bool hasFrame = vr::VRCompositor()->GetFrameTiming(&t, 0);
			auto currentTime = std::chrono::high_resolution_clock::now();
			std::chrono::duration<float> dt = currentTime - lastTime;
			deltaTime = dt.count();
			// If the frame has changed we update, if a frame was redisplayed we update.
			if ((hasFrame && currentFrame != t.m_nFrameIndex) || (hasFrame && t.m_nNumFramePresents != numFramePresents)) {
				currentFrame = t.m_nFrameIndex;
				numFramePresents = t.m_nNumFramePresents;
				lastTime = currentTime;

				UpdateHardwarePositions();
				UpdateRealHardwarePositions();

				if (pmFlags & PlayspaceMoverFlags::Active) {
					CheckPlayspaceMover();
				}

				//Do Math
				for (i = 0; i < 17; i++) {
					trackerStates[i] = trackers[i].CalculatePosition();
				}

				for (j = 0; j < 10; j++) {
					completed = true;
					for (i = 0; i < 17; i++) {
						if (!trackers[i].hasValidPosition) {
							if (trackerStates[i] == 1) {
								completed &= trackers[i].CalculateSingleCameraPosition();
							}
							else {
								//todo
							}
						}
					}
					if (completed) break;
				}

				for (i = 0; i < 17; i++)
					if (trackers[i].hasValidPosition)
						trackers[i].CalculateOrientation();

				if (!trackersOverride) {
					for (i = 0; i < 17; i++) {
						if (PoseTrackers[i]) {
							setOffsetVirtualDevicePosition(trackerIDs[i], trackers[i].position, trackers[i].rotation);
						}
					}
				}

				// Sleep for just under 1/90th of a second, so that maybe the next frame will be available.
				std::this_thread::sleep_for(std::chrono::microseconds(1111));
			}
			else {
				// Still waiting on the next frame, wait less this time.
				std::this_thread::sleep_for(std::chrono::microseconds(1111));
			}
		}

	}
}


void HandleArgs() {
	if (QApplication::arguments().contains("-webDirectory")) {
		int index = QApplication::arguments().indexOf("-webDirectory");
		BaseDirectory = QApplication::arguments().at(index + 1);
	}
}

void endProgram() {
	std::cout << "Driver Stopping...\n" << std::flush;
	active = false;
	calibrating = false;
	OverlayOnClose();
	
	if(MainThread.joinable())
		MainThread.join();
	if (pmFlags & PlayspaceMoverFlags::Active) {
		pmOffset = glm::vec3();
		DisableHardwareOffset();
	}

	if (calibrating && CalibrationThread != nullptr && CalibrationThread->joinable())
		CalibrationThread->join();

	for (int i = 0; i < 17; i++) {
		if (PoseTrackers[i]) {
			deleteVirtualDevice(trackerIDs[i]);
		}
	}

	inputEmulator.disconnect();

	//Save data if needed
	WriteConfig();
	std::cout << "Driver Stopped\n" << std::flush;
}

static bool EndProgram(DWORD signal) {
	switch (signal)
	{
	case CTRL_C_EVENT:
	case CTRL_BREAK_EVENT:
	case CTRL_CLOSE_EVENT:
	case CTRL_LOGOFF_EVENT:
	case CTRL_SHUTDOWN_EVENT:
		std::cout << "Closing..." << std::endl;
		QApplication::quit();
		return true;

	default:
		return false;
	}
}


int main(int argc, char* argv[])
{
#ifdef _WIN32
	if (AttachConsole(ATTACH_PARENT_PROCESS) || AllocConsole()) {
		freopen("CONOUT$", "w", stdout);
		freopen("CONOUT$", "w", stderr);
	}
	else
	{
		freopen("log.txt", "w", stdout);
		freopen("log.txt", "w", stderr);
	}
#endif

	QApplication a(argc, argv);

	HandleArgs();
	SetConsoleCtrlHandler((PHANDLER_ROUTINE)EndProgram, true);

	//temp
	BaseDirectory.append("C:\\VSProjects\\VR-AI-Full-Body-Tracking\\Remote1CamProcessing\\");

	if (!ReadConfig()) {
		std::cout << "Could Not Load Config...\n";
		QJsonObject json;
		json.insert("port", 2674);
		json.insert("windowConfigs", QJsonArray());
		config.setObject(json);
		qDebug() << config;
		WriteConfig();
	}

	StartVR();
	if (pmFlags & PlayspaceMoverFlags::Active) {
		EnableHardwareOffset();
	}
	PoseTracker::InitTrackers();

	VRDashboardOverlay::SharedInstance();
	GetOverlays();


	GetTrackers();

	MainThread = std::thread(MainLoop);

	AIRemoteServer::SharedInstance()->StartServer();
	int i = a.exec();
	endProgram();
	return i;
}
