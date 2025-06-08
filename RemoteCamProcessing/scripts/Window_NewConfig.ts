import { Camera, CameraData } from "./camera-manager";
import { CameraConfig, DefaultConfig } from "./net";
import { findBestMatch } from "string-similarity"

var div_window: HTMLDivElement = document.getElementById("Window_NewConfig") as HTMLDivElement
var el_video: HTMLVideoElement = div_window.querySelector("video")

var select_config: HTMLSelectElement = div_window.querySelector("select#wnc-ex")

var btn_cancel: HTMLButtonElement = div_window.querySelector("button#wnc-cancel")

var btn_new: HTMLButtonElement = div_window.querySelector("button#wnc-new")
var txt_name: HTMLInputElement = div_window.querySelector("input#wnc-name")
var cbx_autostart: HTMLInputElement = div_window.querySelector("input#wnc-autostart")
var num_thresh: HTMLInputElement = div_window.querySelector("input#wnc-threshold")
var cbx_flipHorizontal: HTMLInputElement = div_window.querySelector("input#wnc-flipHorizontal")

export function Window_NewConfig(camID: string, configs: CameraConfig[]): Promise<CameraConfig> {
    return new Promise(async (resolve, reject) => {

        open(camID)

        div_window.onclick = (ev: MouseEvent) => {
            if (ev.target != div_window) return
            close()
            resolve(undefined)
        }
        btn_cancel.onclick = () => {
            close()
            resolve(undefined)
        }

        var camData = await Camera.GetCameraByID(camID)

        populateSelector(camData, configs)
        select_config.onchange = () => {
            if (select_config.value == "") return

            var config = configs[parseInt(select_config.value)]
            config.cameraID = camID

            close()
            resolve(config)
        }

        populateNew(camData)
        btn_new.onclick = () => {
            var config: CameraConfig = DefaultConfig
            config.id = configs.length
            config.cameraID = camID
            config.cameraName = txt_name.value
            config.autostart = cbx_autostart.checked
            config.flip_horizontal = cbx_flipHorizontal.checked
            config.confidenceThreshold = num_thresh.valueAsNumber

            close()
            resolve(config)
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

    select_config.onchange = undefined
}

function populateSelector(camera: CameraData, configs: CameraConfig[]) {
    var noSelectors = configs == undefined || configs.length == 0
    select_config.classList.toggle("d-none", noSelectors)
    if (noSelectors) return

    configs = [...configs]

    select_config.innerHTML = `<option value="">Select existing</option>`

    var matches = findBestMatch(Camera.GetMixedName(camera), configs.map(conf => conf.cameraName)).ratings

    matches.sort((a, b) => b.rating - a.rating)
    matches = matches.map(rat => rat.target)

    var indexesUsed = []
    matches.forEach(name => {
        var index = configs.findIndex((conf, ind) => conf.cameraName == name && !indexesUsed.includes(ind))
        indexesUsed.push(index)
        select_config.innerHTML += `\n<option value=${index}>${name}</option>`
    })
}

function populateNew(camera: CameraData) {
    txt_name.value = Camera.GetMixedName(camera)
    cbx_autostart.checked = DefaultConfig.autostart
    num_thresh.valueAsNumber = DefaultConfig.confidenceThreshold
    cbx_flipHorizontal.checked = DefaultConfig.flip_horizontal
}
