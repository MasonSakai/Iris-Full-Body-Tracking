import { setBackend } from "./pose-detector-factory";
import { Camera } from "./camera-manager";
import { CameraConfig, GetConfigs, NewConfig, sleep, UpdateConfig } from "./util";
import { Window_NewConfig } from "./Window_NewConfig";

let span_fps = document.getElementById("fps")
let div_cameras = document.getElementById("camera-display")
let div_cameras_tmp = document.getElementById("camera-box-tmp")
let select_camera = document.getElementById("camera-select") as HTMLUListElement
let hidden_canvas = document.getElementById("hidden-canvas") as HTMLCanvasElement
let ctx_hidden_canvas = hidden_canvas.getContext("2d", { willReadFrequently: true })

let cameras = [] as Camera[]
async function StartCamera(config: CameraConfig) {
	await new Camera(config).createElement(div_cameras, div_cameras_tmp, (camera: Camera) => {
		camera.startWorker()
		cameras.push(camera)
	})
}

setBackend().then(() => {

	Camera.CameraSelectorCallback = async (id: string) => {

		var configs = await GetConfigs();
		var config = configs.find(config => config.camera_id == id)

		if (config == undefined) {
			config = await Window_NewConfig(id, configs);
			if (config == undefined) {
				Camera.UpdateCameraSelector(select_camera)
				return
			}
			if (config.id >= 0)
				config = await UpdateConfig(config)
			else
				config = await NewConfig(config)
		}

		await StartCamera(config);

		Camera.UpdateCameraSelector(select_camera)
	}

	Camera.UpdateCameraSelector(select_camera).then(cameras => {
		GetConfigs().then(async v => {
			if (cameras == undefined) return;

			for (const config of v) {
				if (config.autostart && cameras.some(cam => cam.id == config.camera_id)) {
					await StartCamera(config)
				}
			}

			Camera.UpdateCameraSelector(select_camera, v)
		});
	})

	AILoop()
})

window.onclose = () => {
	for (var cam of cameras) {
		cam.close();
	}
}

async function AILoop() {
	var start, end, delta;

	while (true) {

		start = (performance || Date).now();
		for (var camera of cameras) {
			await camera.processImage(hidden_canvas, ctx_hidden_canvas)
		}
		end = (performance || Date).now();
		delta = end - start;
		span_fps.innerText = `${delta.toFixed(2)}ms`
		if (delta < 16.66) {
			await sleep(16.66 - delta);
		}
	}
}
