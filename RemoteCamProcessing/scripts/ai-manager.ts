import '@tensorflow/tfjs-backend-webgl';
import '@tensorflow/tfjs-backend-webgpu';
import * as tf from '@tensorflow/tfjs-core';
import * as posedetection from '@tensorflow-models/pose-detection';

export class PoseDetectorFactory {

	width: number

	constructor(width = 640, backend: "webgl" | "webgpu" = "webgpu") {
		tf.setBackend("webgpu");
		this.width = width;
	}

	async createDetector(model_type = "SINGLEPOSE_THUNDER"): Promise<posedetection.PoseDetector> {
		await tf.ready();
		let modelType = posedetection.movenet.modelType[model_type];
		return await posedetection.createDetector(posedetection.SupportedModels.MoveNet, { modelType });
	}

}

export async function GetFilteredPose(video: HTMLVideoElement, detector: posedetection.PoseDetector, threshold: number = 0.3, flipHorizontal: boolean = false, maxPoses: number = 1): Promise<{ [key: string]: { x: number, y: number, score: number } }[]> {
	let raw = await detector.estimatePoses(video, { maxPoses: maxPoses, flipHorizontal: flipHorizontal });
	let poses = []
	for (var p of raw) {
		let keypoints = p.keypoints;
		let filtered = keypoints.filter((data) => {
			return data.score >= threshold;
		});
		let pose = {};
		filtered.forEach((data) => {
			pose[data.name] = {
				x: data.x,
				y: data.y,
				score: data.score
			}
		})
		poses.push(pose)
	}
	return poses;
}