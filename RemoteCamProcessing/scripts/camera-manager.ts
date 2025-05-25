import { time } from "console";
import { GetFilteredPose } from "./ai-manager";
import { PoseDetector } from '@tensorflow-models/pose-detection';

export class Camera {

	el_div: HTMLDivElement
	el_canvas: HTMLCanvasElement
	el_video: HTMLVideoElement
	deviceID: string
	flip_horizontal: boolean = false
	threshold: number = 0.3
	detector: PoseDetector

	constructor(deviceID: string) {
		this.deviceID = deviceID
	}

	createElement(videoReadyCallback: (value: Camera) => void | PromiseLike<void> | undefined = undefined): HTMLDivElement {
		this.el_div = document.createElement("div")
		this.el_div.id = this.deviceID
		this.el_div.className = "camera-card"


		var div_label = document.createElement("div");
		div_label.className = "camera-label"
		Camera.GetCameraByID(this.deviceID).then(v =>
			div_label.innerText = v == undefined ? "ERROR GETTING NAME" : Camera.GetMixedName(v)
		)
		this.el_div.appendChild(div_label)


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
		div_camera.appendChild(this.el_canvas)

		this.el_div.appendChild(div_camera)


		var div_controls = document.createElement("div")
		div_controls.classList = "camera-controls"
		div_controls.innerText = "a"
		this.el_div.appendChild(div_controls)


		return this.el_div
	}


	async processPose() {
		//console.time("detector")
		var data = await GetFilteredPose(this.el_video, this.detector, this.threshold, this.flip_horizontal)
		//console.timeLog("detector", "Got poses!", data)
		
		var ctx = this.el_canvas.getContext("2d");
		ctx.clearRect(0, 0, this.el_canvas.width, this.el_canvas.height)
		ctx.strokeStyle = 'White';
		ctx.lineWidth = 1;

		for (var pose of data) {
			//console.log("pose: ", pose)
			for (var key in pose) {
				//console.log(key)
				let spl = key.split("_");
				if (spl[0] == "right") ctx.fillStyle = "red";
				else if (spl[0] == "left") ctx.fillStyle = "green";
				else ctx.fillStyle = "blue";
				let point = pose[key];
				const circle = new Path2D();
				circle.arc(point.x, point.y, 5, 0, 2 * Math.PI);
				ctx.fill(circle);
				ctx.stroke(circle);

			}
		}
		//console.timeEnd("detector")
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