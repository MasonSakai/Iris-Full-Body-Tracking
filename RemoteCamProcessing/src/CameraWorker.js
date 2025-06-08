import { GetFilteredPose, CreateDetector } from "./pose-detector-factory";
import { IrisSocket_Key } from "./IrisWebClient_keys";
var url;
var detector;
var threshold;
var flip_horizontal;
var image;
var delta = -1;
var socket;
self.onmessage = async function (ev) {
    try {
        var data = ev.data;
        switch (data.key) {
            case IrisSocket_Key.msg_config:
                if (data.url != undefined)
                    url = data.url;
                if (data.threshold != undefined)
                    threshold = data.threshold;
                if (data.flip_horizontal != undefined)
                    flip_horizontal = data.flip_horizontal;
                break;
            case IrisSocket_Key.msg_image:
                image = data.image;
                break;
            case IrisSocket_Key.msg_start:
                StartSocket(data.name);
                CreateDetector().then(d => {
                    detector = d;
                    AILoop();
                });
                break;
            case IrisSocket_Key.msg_socket:
                socket.send(data.message);
                break;
            case IrisSocket_Key.msg_requestParams:
                data.key = IrisSocket_Key.CONFIG_POST;
                data.threshold = threshold;
                data.flip_horizontal = flip_horizontal;
                socket.send(JSON.stringify(data));
                break;
        }
    }
    catch (e) {
        postMessage({
            key: IrisSocket_Key.msg_error,
            error: e
        });
    }
};
self.onerror = (ev) => {
    postMessage({
        key: IrisSocket_Key.msg_error,
        error: ["remote.onerror", ev]
    });
};
self.onmessageerror = (ev) => {
    postMessage({
        key: IrisSocket_Key.msg_error,
        error: ["remote.onmessageerror", ev]
    });
};
async function processPose() {
    var data = {
        key: IrisSocket_Key.POSE,
        delta: avgDelta(delta),
        pose: await GetFilteredPose(image, detector, threshold, flip_horizontal)
    };
    postMessage(data);
    if (socket.readyState == WebSocket.OPEN) {
        socket.send(JSON.stringify(data));
    }
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
function StartSocket(name) {
    socket = new WebSocket(url);
    socket.onopen = function (ev) {
        postMessage({
            key: IrisSocket_Key.msg_socket_event,
            func: "onopen",
            event: {
                type: ev.type,
                timeStamp: ev.timeStamp
            }
        });
        socket.send(JSON.stringify({
            key: IrisSocket_Key.DECLARE,
            name: name
        }));
    };
    socket.onclose = function (ev) {
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
        });
    };
    socket.onerror = function (ev) {
        postMessage({
            key: IrisSocket_Key.msg_socket_event,
            func: "onerror",
            event: {
                type: ev.type,
                timeStamp: ev.timeStamp
            }
        });
    };
    socket.onmessage = function (ev) {
        let data = JSON.parse(ev.data);
        switch (data.key) {
            case IrisSocket_Key.CONFIG_NOTFOUND:
                postMessage({ key: IrisSocket_Key.msg_requestParams });
                break;
            case IrisSocket_Key.IMAGE:
                postMessage(data);
                break;
            default:
                postMessage(data);
                break;
        }
    };
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