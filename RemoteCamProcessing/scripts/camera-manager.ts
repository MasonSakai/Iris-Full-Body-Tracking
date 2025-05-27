import { IrisSocket_Key } from "./IrisWebClient_keys";

export class Camera {

	el_div: HTMLDivElement
	el_canvas: HTMLCanvasElement
	el_video: HTMLVideoElement
	div_label: HTMLDivElement
	span_fps: HTMLSpanElement
	deviceID: string
	flip_horizontal: boolean = false
	threshold: number = 0.3
	ai_worker: Worker
	ctx: CanvasRenderingContext2D
	send_frame: boolean = false

	constructor(deviceID: string) {
		this.deviceID = deviceID
	}

	createElement(videoReadyCallback: (value: Camera) => void | PromiseLike<void> | undefined = undefined): HTMLDivElement {
		this.el_div = document.createElement("div")
		this.el_div.id = this.deviceID
		this.el_div.className = "camera-card"


		this.div_label = document.createElement("div");
		this.div_label.className = "camera-label"
		Camera.GetCameraByID(this.deviceID).then(v =>
			this.div_label.innerText = v == undefined ? "ERROR GETTING NAME" : Camera.GetMixedName(v)
		)
		this.el_div.appendChild(this.div_label)


		var div_camera = document.createElement("div")
		div_camera.className = "camera-display"

		this.el_video = document.createElement("video")
		Camera.GetCameraStream(this.deviceID)
			.then(stream => {
				this.el_video.srcObject = stream
				this.el_video.play()
					.then(() => {
						this.el_canvas.width = this.el_video.videoWidth
						this.el_canvas.height = this.el_video.videoHeight
						if (videoReadyCallback != undefined) videoReadyCallback(this)
					})
			})
		div_camera.appendChild(this.el_video)

		this.el_canvas = document.createElement("canvas")
		this.ctx = this.el_canvas.getContext("2d")
		div_camera.appendChild(this.el_canvas)

		this.el_div.appendChild(div_camera)


		var div_controls = document.createElement("div")
		div_controls.classList = "camera-controls"

		this.span_fps = document.createElement("span")
		this.span_fps.classList = "fps"
		div_controls.appendChild(this.span_fps)

		this.el_div.appendChild(div_controls)


		return this.el_div
	}

	processImage(canvas: HTMLCanvasElement, ctx: CanvasRenderingContext2D) {
		canvas.width = this.el_video.videoWidth
		canvas.height = this.el_video.videoHeight
		ctx.drawImage(this.el_video, 0, 0, this.el_video.videoWidth, this.el_video.videoHeight)
		this.ai_worker.postMessage({
			key: IrisSocket_Key.msg_image,
			image: ctx.getImageData(0, 0, this.el_video.videoWidth, this.el_video.videoHeight)
		})
		if (this.send_frame) {
			this.send_frame = false
			this.ai_worker.postMessage({
				key: IrisSocket_Key.msg_socket,
				message: JSON.stringify({
					key: IrisSocket_Key.IMAGE,
					data: canvas.toDataURL()
				})
			})
		}
	}


	startWorker(url: string) {
		if (typeof (Worker) === "undefined") {
			console.log(`Camera worker ${ this.div_label.innerText } failed`)
			return;
		}

		this.ai_worker = new Worker("CameraWorker.js", { type: "module" })
		this.ai_worker.onmessage = (ev: MessageEvent) => {
			var data = ev.data

			switch (data.key) {
				case IrisSocket_Key.POSE:

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

				case IrisSocket_Key.IMAGE:
					this.send_frame = true
					break;

				case IrisSocket_Key.msg_debug:
					console.log(`Camera worker ${this.div_label.innerText }`, data.message)
					break;
				case IrisSocket_Key.msg_error:
					console.error(`Camera worker ${ this.div_label.innerText } error`, data.error)
					break;

				default:
					console.log(`Camera worker ${ this.div_label.innerText } - ${ data.key }`, data)
					break;

			}
		}
		this.ai_worker.onerror = (ev: ErrorEvent) => {
			console.log(`Camera worker ${ this.div_label.innerText } onerror`, ev)
		}
		this.ai_worker.onmessageerror = (ev: MessageEvent) => {
			console.log(`Camera worker ${ this.div_label.innerText } onmessageerror`, ev)
		}

		this.ai_worker.postMessage({ key: IrisSocket_Key.msg_config, flip_horizontal: this.flip_horizontal, threshold: this.threshold, url: url })
		this.ai_worker.postMessage({ key: IrisSocket_Key.msg_start, name: this.div_label.innerText })
	}

	close() {
		this.ai_worker.terminate()
		this.ai_worker = undefined
	}

	static async GetCameraStream(deviceID: string | undefined = ""): Promise<MediaStream | undefined> {
		if ('mediaDevices' in navigator && 'getUserMedia' in navigator.mediaDevices) {
			let properties: { [key: string]: any } = {
				video: {} /*{
					width: {
						ideal: 640
					},
					height: {
						ideal: 480
					}
				}*/
			}
			if (deviceID) properties.video["deviceId"] = { exact: deviceID };
			return await navigator.mediaDevices.getUserMedia(properties);
		}
		return undefined
	}
	static async GetCamerasByName(deviceName: string): Promise<{ label: string, id: string }[] | undefined> {
		var cameras = await Camera.GetCameras()
		if (!cameras) return undefined
		return cameras.filter(v => v.label == deviceName)
	}
	static async GetCameraByID(deviceID: string): Promise<{ label: string, id: string } | undefined> {
		var cameras = await Camera.GetCameras()
		if (cameras == undefined) return undefined
		return cameras.find(v => v.id == deviceID)
	}

	static async GetCameras(): Promise<{ label: string, id: string }[] | undefined> {
		if (!('mediaDevices' in navigator && 'getUserMedia' in navigator.mediaDevices)) return undefined

		const devices = await navigator.mediaDevices.enumerateDevices();
		const videoDevices = devices.filter(device => device.kind === 'videoinput');
		if (videoDevices[0].deviceId == '') {
			await Camera.GetCameraStream();
			return await Camera.GetCameras();
		}
		return videoDevices.map((videoDevice) => {
			return {
				label: videoDevice.label,
				id: videoDevice.deviceId
			};
		});
	}

	static async UpdateCameraSelector(camSelect: HTMLSelectElement) {
		let cameras = await Camera.GetCameras()
		if (cameras == undefined) return

		cameras = cameras.filter(v => document.getElementById(v.id) == undefined);
		camSelect.innerHTML = `<option value="">Select camera</option>`
		cameras.forEach((camera) => {
			camSelect.innerHTML += `\n<option value=${camera.id}>${Camera.GetMixedName(camera)}</option>`
		});
	}

	static GetMixedName(info: { label: string, id: string }): string {
		return `${info.label.split(" (")[0]} (${info.id.substring(0, 6)})`
	}
}