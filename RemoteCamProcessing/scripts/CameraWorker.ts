import { GetFilteredPose, CreateDetector } from "./pose-detector-factory";
import { PoseDetector } from '@tensorflow-models/pose-detection';
import { Socket, io } from 'socket.io-client';
import { IrisWorkerKey } from "./IrisWebClient_keys";
import { CameraConfig } from "./util"

var config: CameraConfig
var detector: PoseDetector
var image: ImageData
var delta: number = -1
var socket: Socket

self.onmessage = async function (ev: MessageEvent) {
	try {
		var data = ev.data

		switch (data.key) {
			case IrisWorkerKey.msg_config:
				if (data.config != undefined) config = data.config
				break;
			case IrisWorkerKey.msg_image:
				image = data.image
				break;
			case IrisWorkerKey.msg_start:
				StartSocket()
				CreateDetector().then(d => {
					detector = d
					AILoop()
				})
				break;
			case IrisWorkerKey.msg_socket:
				socket.emit(data.ev, data.message)
				break;
			case IrisWorkerKey.msg_requestParams:
				socket.emit("params", data)
				break;
		}
	} catch (e) {
		postMessage({
			key: IrisWorkerKey.msg_error,
			error: e
		})
	}

}
self.onerror = (ev: ErrorEvent) => {
	postMessage({
		key: IrisWorkerKey.msg_error,
		error: ["remote.onerror", ev]
	})
}
self.onmessageerror = (ev: MessageEvent) => {
	postMessage({
		key: IrisWorkerKey.msg_error,
		error: ["remote.onmessageerror", ev]
	})
}

async function processPose() {
	var data = {
		key: IrisWorkerKey.msg_pose,
		delta: avgDelta(delta),
		pose: await GetFilteredPose(image, detector, config.confidence_threshold, config.flip_horizontal)
	}
	postMessage(data)
	if (socket.active) {
		socket.emit('pose', {
			id: config.id,
			time: (performance || Date).now(),
			avg_delta: data.delta,
			pose: data.pose
		})
	}
}

async function AILoop() {
	var start: number, end: number;

	while (!image) { }

	while (true) {
		start = (performance || Date).now();
		await processPose()
		end = (performance || Date).now();
		delta = end - start;
		//if (delta < 16.66) {
		//	await sleep(16.66 - delta);
		//}
	}
}

function StartSocket() {
	socket = io('/camsite', {
		auth: config
	})
	socket.on('connect', () => {
		postMessage({
			key: IrisWorkerKey.msg_socket_event,
			func: "on_connect"
		})
	})
	socket.on('disconnect', (reason: string) => {
		postMessage({
			key: IrisWorkerKey.msg_socket_event,
			func: "on_disconnect",
			event: {
				reason: reason
			}
		})
	})
	socket.on('error', (error) => {
		postMessage({
			key: IrisWorkerKey.msg_socket_event,
			func: "onerror",
			event: {
				error: error
			}
		})
	})

	socket.on('config-not_found', () => {
		postMessage({ key: IrisWorkerKey.msg_requestParams })
	})
	socket.on('image', () => {
		postMessage({ key: IrisWorkerKey.msg_image })
	})
}


function sleep(ms) {
	return new Promise(resolve => setTimeout(resolve, ms));
}

var avgVals = []
var avgIndex = 0
function avgDelta(delta: number): number {

	avgVals[avgIndex] = delta
	avgIndex++
	if (avgIndex >= 100) avgIndex = 0

	return avgVals.reduce((accumulator, currentValue) => accumulator + currentValue, 0) / avgVals.length;
}
