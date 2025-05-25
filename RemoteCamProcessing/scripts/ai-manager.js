import '@tensorflow/tfjs-backend-webgl';
import * as tf from '@tensorflow/tfjs-core';
import * as posedetection from '@tensorflow-models/pose-detection';

export class PoseDetector {

	constructor(width = 640) {
		tf.setBackend("webgl");
		this.width = width;
	}

	async createDetector(model_type = "SINGLEPOSE_THUNDER") {
		await tf.ready();
		let modelType = posedetection.movenet.modelType[model_type];
		this.detector = await posedetection.createDetector(posedetection.SupportedModels.MoveNet, { modelType });
	}

	async getFilteredPose(video, threshold, flipHorizontal) {
		let raw = await this.detector.estimatePoses(video);
		if (raw.length == 0) return {};
		let keypoints = raw[0].keypoints;
		let filtered = keypoints.filter((data) => {
			return data.score >= threshold;
		});
		let pose = {};
		filtered.forEach((data) => {
			pose[data.name] = {
				x: flipHorizontal ? this.width - data.x : data.x,
				y: data.y,
				score: data.score
			}
		})
		return pose;
	}

	tfReady() {
		return tf.ready();
	}
}