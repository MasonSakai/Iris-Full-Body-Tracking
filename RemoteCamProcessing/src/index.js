import { setBackend } from "./pose-detector-factory";
import { Camera } from "./camera-manager";
let span_fps = document.getElementById("fps");
let div_cameras = document.getElementById("camera-display");
let select_camera = document.getElementById("camera-select");
let hidden_canvas = document.getElementById("hidden-canvas");
let ctx_hidden_canvas = hidden_canvas.getContext("2d", { willReadFrequently: true });
let cameras = [];
var port = 2673;
Camera.UpdateCameraSelector(select_camera);
setBackend().then(() => {
    select_camera.onchange = () => {
        if (select_camera.value == "")
            return;
        var camera = new Camera(select_camera.value);
        div_cameras.appendChild(camera.createElement(() => {
            camera.startWorker(window.location.protocol + "//" + window.location.hostname + ":" + port);
            cameras.push(camera);
            //setInterval(() => {
            //	var context = camera.el_canvas.getContext("2d")
            //	context.drawImage(camera.el_video, 0, 0, camera.el_canvas.width, camera.el_canvas.height)
            //	console.log({ w: camera.el_canvas.width, h: camera.el_canvas.height })
            //	window.location.href = camera.el_canvas.toDataURL("image/png").replace("image/png", "image/octet-stream")
            //}, 5000)
        }));
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