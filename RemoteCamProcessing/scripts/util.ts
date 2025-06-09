
export type CameraConfig = {
	id: number,
	cameraName: string,
	cameraID: string,
	autostart: boolean,
	confidenceThreshold: number,
	flip_horizontal: boolean
}

export const DefaultConfig: CameraConfig = {
	id: -1,
	cameraName: "",
	cameraID: "",
	autostart: false,
	confidenceThreshold: 0.3,
	flip_horizontal: false
};

export async function fetchAsync(port: string) {
	let response = await fetch(port);
	let data = await response.json();
	return data;
}
export async function fetchAsyncText(port: string) {
	let response = await fetch(port);
	let data = await response.text();
	return data;
}
export async function putAsync(port: string, data: any) {
	return await fetch(port, {
		method: 'PUT',
		headers: {
			'Content-type': 'application/json'
		},
		body: JSON.stringify(data)
	});
}
export async function putAsyncText(port: string, data: string) {
	return await fetch(port, {
		method: 'PUT',
		headers: {
			'Content-type': 'text/text'
		},
		body: data
	});
}

export async function sendPose(id: number, pose) {
	await putAsync("poseData", {
		id: id,
		pose: pose
	});
}
export async function sendSize(id: number, video: HTMLVideoElement) {
	let rect = video.getBoundingClientRect();
	await putAsync("cameraSize", {
		id: id,
		width: rect.width,
		height: rect.height
	});
}
export async function sendStart(id: number) {
	await putAsyncText("start", id.toString());
}
export async function sendConnect(id: number) {
	await putAsyncText("connect", id.toString());
}

export async function PutConfig(config: CameraConfig) {
	putAsync("config", config)
}
export async function GetConfigs(): Promise<CameraConfig[] | undefined> {
	try {
		var response = await fetch("config.json");
		let data = await response.json();
		//add fail check
		data = data.windowConfigs;
		for (var i = 0; i < data.length; i++) { data[i].id = i }
		return data;
		//console.log(configs);
		//numConfigs = configs.length;
		//configSelect.innerHTML = "<option value=-1>Select:</option>\n<option value=-2>Create New</option>";
		//for (let i = 0; i < numConfigs; i++) {
		//	configSelect.innerHTML += `\n<option value=${i}>${i}</option>`;
		//}
	} catch (err) {
		console.error(err);
		return;
	}
}

export function CreateCheckbox(id: string, text: string): [HTMLDivElement, HTMLInputElement] {
	var div = document.createElement("div")
	div.className = "form-check"

	var cbx = document.createElement("input")
	cbx.className = "form-check-input"
	cbx.type = "checkbox"
	cbx.name = id
	cbx.id = id
	div.appendChild(cbx)

	var lbl = document.createElement("label")
	lbl.className = "form-check-label"
	lbl.htmlFor = id
	lbl.innerText = text
	div.appendChild(lbl)

	return [div, cbx]
}

export function CreateRange(id: string, text: string): [HTMLLabelElement, HTMLInputElement] {

	var lbl = document.createElement("label")
	lbl.className = "form-label"
	lbl.htmlFor = id
	lbl.innerText = text

	var rng = document.createElement("input")
	rng.className = "form-range"
	rng.type = "range"
	rng.name = id
	rng.id = id

	return [lbl, rng]
}