import { GetFilteredPose, CreateDetector } from "./pose-detector-factory";
var detector;
var threshold;
var flip_horizontal;
var image;
var delta = -1;
self.onmessage = async function (ev) {
    try {
        var data = ev.data;
        switch (data.type) {
            case "config":
                threshold = data.threshold;
                flip_horizontal = data.flip_horizontal;
                break;
            case "video":
                image = data.image;
                break;
            case "start":
                CreateDetector().then(d => {
                    detector = d;
                    AILoop();
                });
                break;
        }
    }
    catch (e) {
        postMessage({
            type: "error",
            error: e
        });
    }
};
self.onerror = (ev) => {
    postMessage({
        type: "error",
        error: ["remote.onerror", ev]
    });
};
self.onmessageerror = (ev) => {
    postMessage({
        type: "error",
        error: ["remote.onmessageerror", ev]
    });
};
async function processPose() {
    var data = {
        type: "pose",
        delta: avgDelta(delta),
        pose: await GetFilteredPose(image, detector, threshold, flip_horizontal)
    };
    postMessage(data);
    //send to socket
}
async function AILoop() {
    var start, end;
    while (!image) { }
    while (true) {
        start = (performance || Date).now();
        await processPose();
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
var avgVals = [];
var avgIndex = 0;
function avgDelta(delta) {
    avgVals[avgIndex] = delta;
    avgIndex++;
    if (avgIndex >= 100)
        avgIndex = 0;
    return avgVals.reduce((accumulator, currentValue) => accumulator + currentValue, 0) / avgVals.length;
}
//# sourceMappingURL=CameraWorker.js.map