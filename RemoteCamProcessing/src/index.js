import { setBackend } from "./pose-detector-factory";
import { Camera } from "./camera-manager";
import { PutConfig, GetConfigs, sendConnect, sendSize, DefaultConfig } from "./net";
let span_fps = document.getElementById("fps");
let div_cameras = document.getElementById("camera-display");
let select_camera = document.getElementById("camera-select");
let hidden_canvas = document.getElementById("hidden-canvas");
let ctx_hidden_canvas = hidden_canvas.getContext("2d", { willReadFrequently: true });
let cameras = [];
function StartCamera(config) {
    var camera = new Camera(config);
    div_cameras.appendChild(camera.createElement(async (camera) => {
        await sendConnect(config.id);
        await sendSize(config.id, camera.el_video);
        camera.startWorker();
        cameras.push(camera);
    }));
}
setBackend().then(() => {
    Camera.UpdateCameraSelector(select_camera).then(cameras => {
        GetConfigs().then(v => {
            if (cameras == undefined)
                return;
            v.forEach(config => {
                if (config.autostart && cameras.some(cam => cam.id == config.cameraID)) {
                    StartCamera(config);
                }
            });
            Camera.UpdateCameraSelector(select_camera);
        });
    });
    select_camera.onchange = async () => {
        if (select_camera.value == "")
            return;
        var configs = await GetConfigs();
        var config = configs.find(config => config.cameraID == select_camera.value);
        if (config == undefined) {
            config = DefaultConfig;
            config.id = configs.length;
            config.cameraName = select_camera.options[select_camera.selectedIndex].text;
            config.cameraID = select_camera.value;
            await PutConfig(config);
        }
        StartCamera(config);
        select_camera.value = "";
        Camera.UpdateCameraSelector(select_camera);
    };
    AILoop();
});
window.onclose = () => {
    for (var cam of cameras) {
        cam.close();
    }
};
async function AILoop() {
    var start, end, delta;
    while (true) {
        start = (performance || Date).now();
        for (var camera of cameras) {
            await camera.processImage(hidden_canvas, ctx_hidden_canvas);
        }
        end = (performance || Date).now();
        delta = end - start;
        span_fps.innerText = `${delta.toFixed(2)}ms`;
        if (delta < 16.66) {
            await sleep(16.66 - delta);
        }
    }
}
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}
//# sourceMappingURL=index.js.map