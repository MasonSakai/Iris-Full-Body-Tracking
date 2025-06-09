import { GetFilteredPose, CreateDetector } from "./pose-detector-factory";
import { PoseDetector } from '@tensorflow-models/pose-detection';
import { IrisSocket_Key } from "./IrisWebClient_keys";
import { sendPose, CameraConfig, sendStart } from "./util"

var config: CameraConfig
var detector: PoseDetector
var image: ImageData
var delta: number = -1

self.onmessage = async function (ev: MessageEvent) {
	try {
		var data = ev.data

		switch (data.key) {
			case IrisSocket_Key.msg_config:
				config = data.config
				break;
			case IrisSocket_Key.msg_image:
				image = data.image
				break;
			case IrisSocket_Key.msg_start:
				sendStart(config.id)
				CreateDetector().then(d => {
					detector = d
					AILoop()
				})
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
	var pose = await GetFilteredPose(image, detector, config.confidenceThreshold, config.flip_horizontal);
	var data = {
		key: IrisSocket_Key.msg_pose,
		delta: avgDelta(delta),
		pose: pose
	}
	postMessage(data)
	await sendPose(config.id, pose)
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
