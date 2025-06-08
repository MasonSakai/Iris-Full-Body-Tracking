import '@tensorflow/tfjs-backend-webgl';
import '@tensorflow/tfjs-backend-webgpu';
import * as tf from '@tensorflow/tfjs-core';
import * as posedetection from '@tensorflow-models/pose-detection';
export function setBackend(backend = "webgpu") {
    return tf.setBackend("webgpu");
}
export function tfReady() { return tf.ready(); }
export async function CreateDetector(model_type = "SINGLEPOSE_THUNDER") {
    await tf.ready();
    let modelType = posedetection.movenet.modelType[model_type];
    return await posedetection.createDetector(posedetection.SupportedModels.MoveNet, { modelType });
}
export async function GetFilteredPose(image, detector, threshold = 0.3, flipHorizontal = false, maxPoses = 1) {
    let raw = await detector.estimatePoses(image, { maxPoses: maxPoses, flipHorizontal: flipHorizontal });
    let poses = [];
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
            };
        });
        poses.push(pose);
    }
    return poses;
}
//# sourceMappingURL=pose-detector-factory.js.map