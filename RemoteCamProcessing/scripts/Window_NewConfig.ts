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

		var downOn = false
		div_window.onmousedown = (ev: MouseEvent) => {
			downOn = ev.target == div_window
		}
		div_window.onmouseup = (ev: MouseEvent) => {
			if (downOn) {
				if (ev.target == div_window) {
					close()
					resolve(undefined)
				}
			}
			downOn = false;
		}
		btn_cancel.onclick = () => {
			close()
			resolve(undefined)
		}

		var camData = await Camera.GetCameraByID(camID)

		await populateSelector(camData, configs, resolve)

		populateNew(camData)
		btn_new.onclick = () => {
			var config: CameraConfig = DefaultConfig
			config.camera_id = camID
			config.name = txt_name.value
			config.autostart = cbx_autostart.checked
			config.flip_horizontal = cbx_flipHorizontal.checked
			config.confidence_threshold = num_thresh.valueAsNumber

			close()
			resolve(config)
		}
		txt_name.oninput = () => {
			btn_new.disabled = configs.some(c => c.name == txt_name.value)
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

async function populateSelector(camera: CameraData, configs: CameraConfig[], resolve) {
	select_config.innerHTML = ""

	configs = configs.filter(v => document.body.querySelector(`.card[config-id="${v.id}"]`) == undefined)

	var noSelectors = configs == undefined || configs.length == 0
	select_config_btn.classList.toggle("d-none", noSelectors)
	if (noSelectors) return

	var matches = findBestMatch(Camera.GetMixedName(camera), configs.map(conf => conf.name)).ratings

	matches.sort((a, b) => b.rating - a.rating)

	var cams = await Camera.GetCameras()
	var indexesUsed = []
	matches = matches.map(rat => {
		var index = configs.findIndex((conf, ind) => conf.name == rat.target && !indexesUsed.includes(ind))
		indexesUsed.push(index)

		return {
			config: configs[index],
			hasID: cams.some(v => v.id == configs[index].camera_id)
		}
	}) as { config: CameraConfig, hasID: Boolean }[]

	var seenFound = false
	var passedFound = false
	matches
		.sort((a: { config: CameraConfig, hasID: Boolean }, b: { config: CameraConfig, hasID: Boolean }) => {
			var va = a.hasID ? 1 : 0
			var vb = b.hasID ? 1 : 0
			return va - vb;
		})
		.forEach((v: { config: CameraConfig, hasID: Boolean }) => {
			if (!v.hasID) {
				seenFound = true
			}
			else if (seenFound && !passedFound) {
				passedFound = true
				var li = document.createElement("li")
				var hr = document.createElement("hr")
				hr.className = "dropdown-divider"
				li.appendChild(hr)
				select_config.appendChild(li)
			}

			var li = document.createElement("li")
			var btn = document.createElement("button")
			btn.type = "button"
			btn.className = "dropdown-item"
			btn.innerText = v.config.name
			btn.onclick = () => {
				v.config.camera_id = camera.id
				close()
				resolve(v.config)
			}
			li.appendChild(btn)
			select_config.appendChild(li)
		})
}

function populateNew(camera: CameraData) {
	txt_name.value = Camera.GetMixedName(camera)
	cbx_autostart.checked = DefaultConfig.autostart
	num_thresh.valueAsNumber = DefaultConfig.confidence_threshold
	cbx_flipHorizontal.checked = DefaultConfig.flip_horizontal
}
