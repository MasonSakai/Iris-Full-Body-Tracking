import { IrisWorkerKey } from "./IrisWebClient_keys";
import { CameraConfig, GetConfigs, sleep, UpdateConfig } from "./util"

export type CameraData = { label: string, id: string }
export class Camera {

	el_card: HTMLDivElement
	el_canvas: HTMLCanvasElement
	el_video: HTMLVideoElement
	span_fps: HTMLSpanElement
	config: CameraConfig
	ai_worker: Worker
	ctx: CanvasRenderingContext2D
	send_frame: {} | string | false | undefined = false

	constructor(config: CameraConfig) {
		this.config = config
	}

	async createElement(parent: HTMLElement, tmpParent: HTMLElement, videoReadyCallback: (value: Camera) => void | PromiseLike<void> | undefined = undefined) {
		var resp = await fetch(`cameras/${this.config.id}/cam_box`)
		tmpParent.innerHTML = await resp.text()

		this.el_card = tmpParent.querySelector(`[camera-id="${this.config.camera_id}"]`)

		var span_label = this.el_card.querySelector(`.lbl-name`) as HTMLSpanElement
		var btn_label = this.el_card.querySelector(`.btn-name`) as HTMLButtonElement
		btn_label.onclick = () => {
			var name = prompt("Rename camera", this.config.name)
			if (name == null || name === "") return
			if (name == this.config.name) return

			this.config.name = name
			span_label.innerText = name
			this.updateConfig()
		}


		this.el_video = this.el_card.querySelector("video")
		Camera.GetCameraStream(this.config.camera_id)
			.then(stream => {
				this.el_video.srcObject = stream
				this.el_video.play()
					.then(() => {
						this.el_canvas.width = this.el_video.videoWidth
						this.el_canvas.height = this.el_video.videoHeight
						if (videoReadyCallback != undefined) videoReadyCallback(this)
					})
			})

		this.el_canvas = this.el_card.querySelector("canvas")
		this.ctx = this.el_canvas.getContext("2d")


		var cbx_autostart = this.el_card.querySelector(`#autostart-${this.config.camera_id}`) as HTMLInputElement
		cbx_autostart.checked = this.config.autostart
		cbx_autostart.onchange = () => {
			this.config.autostart = cbx_autostart.checked
			this.updateConfig()
		}

		var cbx_flipHorizontal = this.el_card.querySelector(`#flipHorizontal-${this.config.camera_id}`) as HTMLInputElement
		cbx_flipHorizontal.checked = this.config.flip_horizontal
		cbx_flipHorizontal.onchange = () => {
			this.config.flip_horizontal = cbx_flipHorizontal.checked
			this.updateConfig()
		}

		var range_threshold = this.el_card.querySelector(`#threshold-${this.config.camera_id}`) as HTMLInputElement
		range_threshold.valueAsNumber = this.config.confidence_threshold
		range_threshold.oninput = () => {
			this.config.confidence_threshold = range_threshold.valueAsNumber
			this.ai_worker.postMessage({ key: IrisWorkerKey.msg_config, config: this.config })
		}
		range_threshold.onchange = () => {
			this.config.confidence_threshold = range_threshold.valueAsNumber
			this.updateConfig()
		}

		this.span_fps = this.el_card.querySelector(`.fps`) as HTMLDivElement

		parent.appendChild(this.el_card)
		return this.el_card
	}

	async processImage(canvas: HTMLCanvasElement, ctx: CanvasRenderingContext2D) {
		canvas.width = this.el_video.videoWidth
		canvas.height = this.el_video.videoHeight
		ctx.drawImage(this.el_video, 0, 0)
		this.ai_worker.postMessage({
			key: IrisWorkerKey.msg_image,
			image: ctx.getImageData(0, 0, this.el_video.videoWidth, this.el_video.videoHeight)
		})

		if (this.send_frame != false) {
			var props = this.send_frame
			this.send_frame = false

			var stream: MediaStream = undefined

			try {

				stream = await Camera.GetCameraStream(this.config.camera_id, props)
				if (stream) {
					var settings = stream.getVideoTracks()[0].getSettings()
					var vid_settings = (this.el_video.srcObject as MediaStream).getVideoTracks()[0].getSettings()
					var dif = settings != vid_settings && (settings.width > vid_settings.width || settings.height > vid_settings.height)
					if (!dif) {
						props['deviceId'] = undefined
						throw new Error(`Could not get new settings (${JSON.stringify(props)}), using existing stream (${settings.width}, ${settings.height}). Not actually an error`)
					}

					console.log(`Got new settings(${settings.width}, ${settings.height}), but not implimented yet`)
				}

			} catch (e) {
				console.error(e.message)
			}

			//this.ai_worker.postMessage({
			//	key: IrisWorkerKey.msg_socket,
			//	ev: 'image',
			//	message: canvas.toDataURL()
			//})
			fetch(`cameras/${this.config.id}/image`, {
				method: 'POST',
				body: canvas.toDataURL()
			})

			if (stream) {
				stream.getTracks().forEach(t => t.stop())
			}

		}
	}

	updateConfig() {
		this.ai_worker.postMessage({ key: IrisWorkerKey.msg_config, config: this.config })
		UpdateConfig(this.config)
	}

	startWorker() {
		if (typeof (Worker) === "undefined") {
			console.log(`Camera worker ${ this.config.name } failed`)
			return;
		}

		this.ai_worker = new Worker("CameraWorker.js", { type: "module" })
		this.ai_worker.onmessage = (ev: MessageEvent) => {
			var data = ev.data

			switch (data.key) {
				case IrisWorkerKey.msg_pose:

					this.span_fps.innerText = `${Math.floor(1000 / data.delta)}fps (${data.delta.toFixed(1)}ms)`

					this.ctx.clearRect(0, 0, this.el_canvas.width, this.el_canvas.height)
					this.ctx.strokeStyle = 'White';
					this.ctx.lineWidth = 1;
					for (var pose of data.pose) {
						for (var key in pose) {
							let spl = key.split("_");
							if (spl[0] == "right") this.ctx.fillStyle = "red";
							else if (spl[0] == "left") this.ctx.fillStyle = "green";
							else this.ctx.fillStyle = "blue";
							let point = pose[key];
							const circle = new Path2D();
							circle.arc(point.x, point.y, 5, 0, 2 * Math.PI);
							this.ctx.fill(circle);
							this.ctx.stroke(circle);

						}
					}
					break;

				case IrisWorkerKey.msg_image:
					this.send_frame = data.constraints
					break;

				case IrisWorkerKey.msg_requestParams:
					Camera.GetCameraByID(this.config.camera_id).then(async v => {
						data.name = this.config.name
						data.camera_name = Camera.GetMixedName(v)

						var stream = this.el_video.srcObject as MediaStream
						if (stream) {
							data.settings = stream.getVideoTracks()[0].getSettings()
						}

						this.ai_worker.postMessage(data)
					})
					break;

				case IrisWorkerKey.msg_requestCaps: {
					var stream = this.el_video.srcObject as MediaStream
					if (stream) {
						this.ai_worker.postMessage({
							key: IrisWorkerKey.msg_requestCaps,
							caps: stream.getVideoTracks()[0].getCapabilities()
						})
					}
					break;
				}

				case IrisWorkerKey.msg_debug:
					console.log(`Camera worker ${this.config.name }`, data.message)
					break;
				case IrisWorkerKey.msg_error:
					console.error(`Camera worker ${ this.config.name } error`, data.error)
					break;

				default:
					//console.log(`Camera worker ${ this.config.name } - ${ data.key }`, data)
					break;

			}
		}
		this.ai_worker.onerror = (ev: ErrorEvent) => {
			console.log(`Camera worker ${ this.config.name } onerror`, ev)
		}
		this.ai_worker.onmessageerror = (ev: MessageEvent) => {
			console.log(`Camera worker ${ this.config.name } onmessageerror`, ev)
		}

		this.ai_worker.postMessage({ key: IrisWorkerKey.msg_config, config: this.config })
		this.ai_worker.postMessage({ key: IrisWorkerKey.msg_start })
	}

	close() {
		this.ai_worker.terminate()
		this.ai_worker = undefined
	}

	static async GetCameraStream(deviceID: string | undefined = "", props: {} = { width: 640, height: 480 }): Promise<MediaStream | undefined> {
		if ('mediaDevices' in navigator && 'getUserMedia' in navigator.mediaDevices) {
			let properties: { [key: string]: any } = {
				video: props
			}
			if (deviceID) properties.video["deviceId"] = { exact: deviceID };
			return await navigator.mediaDevices.getUserMedia(properties);
		}
		return undefined
	}
	static async GetCamerasByName(deviceName: string): Promise<CameraData[] | undefined> {
		var cameras = await Camera.GetCameras()
		if (!cameras) return undefined
		return cameras.filter(v => v.label == deviceName)
	}
	static async GetCameraByID(deviceID: string): Promise<CameraData | undefined> {
		var cameras = await Camera.GetCameras()
		if (cameras == undefined) return undefined
		return cameras.find(v => v.id == deviceID)
	}

	static async GetCameras(): Promise<CameraData[] | undefined> {
		if (!('mediaDevices' in navigator && 'getUserMedia' in navigator.mediaDevices)) return undefined

		const devices = await navigator.mediaDevices.enumerateDevices();
		const videoDevices = devices.filter(device => device.kind === 'videoinput');
		if (videoDevices[0].deviceId == '') {
			(await Camera.GetCameraStream()).getTracks().forEach(t => t.stop());
			return await Camera.GetCameras();
		}
		return videoDevices.map((videoDevice) => {
			return {
				label: videoDevice.label,
				id: videoDevice.deviceId
			};
		});
	}

	static CameraSelectorCallback = undefined
	static async UpdateCameraSelector(camSelect: HTMLUListElement, configs: CameraConfig[] | undefined = undefined): Promise<CameraData[] | undefined> {
		let cameras = await Camera.GetCameras()
		if (cameras == undefined) return

		if (configs == undefined)
			configs = await GetConfigs()

		var passedConfigs = false
		var seenConfigs = false
		camSelect.innerHTML = ""
		cameras
			.filter(v => document.querySelector(`.card[camera-id="${v.id}"]`) == undefined)
			.sort((a: CameraData, b: CameraData) => {
				var va = configs.find(v => v.camera_id == a.id) != undefined ? 1 : 0
				var vb = configs.find(v => v.camera_id == b.id) != undefined ? 1 : 0
				return vb - va;
			})
			.forEach((camera) => {
				var name = Camera.GetMixedName(camera)
				var config = configs.find(v => v.camera_id == camera.id)
				if (config != undefined) {
					name = config.name
					seenConfigs = true
				}
				else if (seenConfigs && !passedConfigs) {
					passedConfigs = true
					var li = document.createElement("li")
					var hr = document.createElement("hr")
					hr.className = "dropdown-divider"
					li.appendChild(hr)
					camSelect.appendChild(li)
				}
				var li = document.createElement("li")
				var btn = document.createElement("button")
				btn.className = "dropdown-item"
				btn.type = "button"
				btn.innerText = name
				btn.onclick = () => {
					if (this.CameraSelectorCallback)
						this.CameraSelectorCallback(camera.id)
				}
				li.appendChild(btn)
				camSelect.appendChild(li)
			});

		return cameras;
	}

	static GetMixedName(info: { label: string, id: string }): string {
		return `${info.label.split(" (")[0]} (${info.id.substring(0, 6)})`
	}
}