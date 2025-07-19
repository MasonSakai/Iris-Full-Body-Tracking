import { GetFilteredPose, CreateDetector } from "./pose-detector-factory";
import { PoseDetector } from '@tensorflow-models/pose-detection';
import { IrisSocket_Key } from "./IrisWebClient_keys";
import { CameraConfig } from "./util"

var url: string
var config: CameraConfig
var detector: PoseDetector
var image: ImageData
var delta: number = -1
var socket: WebSocket

self.onmessage = async function (ev: MessageEvent) {
	try {
		var data = ev.data

		switch (data.key) {
			case IrisSocket_Key.msg_config:
				if (data.config != undefined) config = data.config
				if (data.url != undefined) url = data.url
				break;
			case IrisSocket_Key.msg_image:
				image = data.image
				break;
			case IrisSocket_Key.msg_start:
				StartSocket()
				CreateDetector().then(d => {
					detector = d
					AILoop()
				})
				break;
			case IrisSocket_Key.msg_socket:
				socket.send(data.message)
				break;
			case IrisSocket_Key.msg_requestParams:
				data.key = IrisSocket_Key.CONFIG_POST
				socket.send(JSON.stringify(data))
				break;
		}
	} catch (e) {
		postMessage({
			key: IrisSocket_Key.msg_error,
			error: e
		})
	}

}
self.onerror = (ev: ErrorEvent) => {
	postMessage({
		key: IrisSocket_Key.msg_error,
		error: ["remote.onerror", ev]
	})
}
self.onmessageerror = (ev: MessageEvent) => {
	postMessage({
		key: IrisSocket_Key.msg_error,
		error: ["remote.onmessageerror", ev]
	})
}

async function processPose() {
	var data = {
		key: IrisSocket_Key.POSE,
		delta: avgDelta(delta),
		pose: await GetFilteredPose(image, detector, config.confidence_threshold, config.flip_horizontal)
	}
	postMessage(data)
	if (socket.readyState == WebSocket.OPEN) {
		socket.send(JSON.stringify(data))
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
	socket = new WebSocket(url)
	socket.onopen = function (ev: Event) {
		postMessage({
			key: IrisSocket_Key.msg_socket_event,
			func: "onopen",
			event: {
				type: ev.type,
				timeStamp: ev.timeStamp
			}
		})

		socket.send(JSON.stringify({
			key: IrisSocket_Key.DECLARE,
			id: config.id
		}))
	}
	socket.onclose = function (ev: CloseEvent) {
		postMessage({
			key: IrisSocket_Key.msg_socket_event,
			func: "onclose",
			event: {
				type: ev.type,
				timeStamp: ev.timeStamp,
				code: ev.code,
				reason: ev.reason,
				wasClean: ev.wasClean
			}
		})
	}
	socket.onerror = function (ev: Event) {
		postMessage({
			key: IrisSocket_Key.msg_socket_event,
			func: "onerror",
			event: {
				type: ev.type,
				timeStamp: ev.timeStamp
			}
		})
	}

	socket.onmessage = function (ev: MessageEvent) {
		let data = JSON.parse(ev.data)

		switch (data.key) {
			case IrisSocket_Key.CONFIG_NOTFOUND:
				postMessage({ key: IrisSocket_Key.msg_requestParams })
				break;

			case IrisSocket_Key.IMAGE:
				postMessage(data)
				break;


			default:
				postMessage(data)
				break
		}
	}

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
