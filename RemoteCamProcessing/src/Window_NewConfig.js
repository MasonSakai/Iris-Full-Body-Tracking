import { Camera } from "./camera-manager";
var div_window = document.getElementById("Window_NewConfig");
var el_video = div_window.querySelector("video");
export function Window_NewConfig(camID, configs) {
    return new Promise(async (resolve, reject) => {
        open(camID);
        div_window.onclick = (ev) => {
            if (ev.target != div_window)
                return;
            close();
            resolve(undefined);
        };
    });
}
async function open(camID) {
    div_window.classList.remove("d-none");
    el_video.srcObject = await Camera.GetCameraStream(camID);
    await el_video.play();
}
function close() {
    var mediaStream = el_video.srcObject;
    if (mediaStream) {
        const tracks = mediaStream.getTracks();
        tracks.forEach(track => track.stop());
        el_video.srcObject = null;
    }
    div_window.classList.add("d-none");
    div_window.onkeydown = undefined;
}
//# sourceMappingURL=Window_NewConfig.js.map