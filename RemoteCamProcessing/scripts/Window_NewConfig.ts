import { Camera, CameraData } from "./camera-manager";
import { CameraConfig, DefaultConfig } from "./util";
import { findBestMatch } from "string-similarity"

var div_window: HTMLDivElement = document.getElementById("Window_NewConfig") as HTMLDivElement
var el_video: HTMLVideoElement = div_window.querySelector("video")

var select_config: HTMLUListElement = div_window.querySelector("ul#wnc-ex")
var select_config_btn: HTMLButtonElement = select_config.previousElementSibling as HTMLButtonElement

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

		populateSelector(camData, configs, resolve)

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

function populateSelector(camera: CameraData, configs: CameraConfig[], resolve) {
	while (select_config.firstChild) {
		select_config.removeChild(select_config.lastChild)
	}

	configs = configs.filter(v => document.body.querySelector(`.card[config-id="${v.id}"]`) == undefined)

	var noSelectors = configs == undefined || configs.length == 0
	select_config_btn.classList.toggle("d-none", noSelectors)
	if (noSelectors) return


	var matches = findBestMatch(Camera.GetMixedName(camera), configs.map(conf => conf.cameraName)).ratings

	matches.sort((a, b) => b.rating - a.rating)
	matches = matches.map(rat => rat.target)

	var indexesUsed = []
	matches.forEach(name => {
		var index = configs.findIndex((conf, ind) => conf.cameraName == name && !indexesUsed.includes(ind))
		indexesUsed.push(index)

		var li = document.createElement("li")
		var btn = document.createElement("button")
		btn.type = "button"
		btn.className = "dropdown-item"
		btn.innerText = name
		btn.onclick = () => {
			var config = configs[index]
			config.cameraID = camera.id
			close()
			resolve(config)
		}
		li.appendChild(btn)
		select_config.appendChild(li)
	})
}

function populateNew(camera: CameraData) {
	txt_name.value = Camera.GetMixedName(camera)
	cbx_autostart.checked = DefaultConfig.autostart
	num_thresh.valueAsNumber = DefaultConfig.confidenceThreshold
	cbx_flipHorizontal.checked = DefaultConfig.flip_horizontal
}
