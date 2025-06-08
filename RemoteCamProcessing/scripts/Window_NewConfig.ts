import { Camera } from "./camera-manager";
import { CameraConfig, DefaultConfig } from "./net";

var div_window: HTMLDivElement = document.getElementById("Window_NewConfig") as HTMLDivElement
var el_video: HTMLVideoElement = div_window.querySelector("video")

export function Window_NewConfig(camID: string, configs: CameraConfig[]): Promise<CameraConfig> {
    return new Promise(async (resolve, reject) => {

        open(camID)

        div_window.onclick = (ev: MouseEvent) => {
            if (ev.target != div_window) return
            close()
            resolve(undefined)
        }
    })
}

async function open(camID: string) {
    div_window.classList.remove("d-none")

    el_video.srcObject = await Camera.GetCameraStream(camID)
    await el_video.play()
}

function close() {
    var mediaStream = el_video.srcObject as MediaStream;

    if (mediaStream) {
        const tracks = mediaStream.getTracks()
        tracks.forEach(track => track.stop())
        el_video.srcObject = null
    }

    div_window.classList.add("d-none")
    div_window.onkeydown = undefined
}