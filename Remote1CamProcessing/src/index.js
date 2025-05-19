
const { Camera } = require("./camera-manager");
const { PoseDetector } = require("./ai-manager");


const controlPanel = document.getElementsByClassName("control-panel")[0];

const lblState = document.getElementById("lbl-state");

const btnStart = document.getElementById("btn-start");
const btnStop = document.getElementById("btn-stop");
const cbxAutostart = document.getElementById("cbx-autostart");

const camSelect = document.getElementById("camera-select");
const btnCamRef = document.getElementById("btn-camref");
const video = document.getElementsByTagName("video")[0];
const canvas = document.getElementsByTagName("canvas")[0];

const btnApply = document.getElementById("btn-apply");
const btnCancel = document.getElementById("btn-cancel");
const btnReset = document.getElementById("btn-reset");
const configSelect = document.getElementById("config-select");
const lblPutState = document.getElementById("lbl-put-state");
var lblPutStateTimeout;

const width = video.clientWidth;
console.log(width);

lblState.innerHTML = "<i>Loading Camera...</i>";

const camera = new Camera();
const poseDetector = new PoseDetector(true, width);

lblState.innerHTML = "<i>Loading...</i>";

const DefaultConfig = {
	id: -1,
	cameraName: "",
	cameraID: "",
	autostart: false,
	confidenceThreshold: 0.3
};
let config = DefaultConfig;
let configUpdate = {};

var activeState = false;

var numConfigs = 0;

async function fetchAsync(port) {
	let response = await fetch(port);
	let data = await response.json();
	return data;
}
async function fetchAsyncText(port) {
	let response = await fetch(port);
	let data = await response.text();
	return data;
}
async function putAsync(port, data) {
	return await fetch(port, {
		method: 'PUT',
		headers: {
			'Content-type': 'application/json'
		},
		body: JSON.stringify(data)
	});
}
async function putAsyncText(port, data) {
	return await fetch(port, {
		method: 'PUT',
		headers: {
			'Content-type': 'text/text'
		},
		body: data
	});
}

function hidePutState() {
	lblPutState.classList.add("d-none");
}
function setPutState(text, timeout) {
	lblPutState.innerHTML = text;
	if (lblPutStateTimeout) clearTimeout(lblPutStateTimeout);
	lblPutState.classList.remove("d-none");
	lblPutStateTimeout = setTimeout(hidePutState, timeout);
}

function applyConfigChange() {
	let madeChange = false;
	let hadError = false;
	if ("autostart" in configUpdate) {
		madeChange = true;
		config.autostart = configUpdate.autostart;
		cbxAutostart.checked = config.autostart;
	}
	if ("cameraID" in configUpdate) {
		madeChange = true;
		config.cameraID = configUpdate.cameraID;
		config.cameraName = configUpdate.cameraName;
		if (configUpdate.cameraID != "") {
			camSelect.value = configUpdate.cameraID;
			if (activeState) {
				camera.getCameraStream(configUpdate.cameraID).then((cam) => {
					video.srcObject = cam;
					resizeCanvas();
				});
			}
		} else {
			video.srcObject = undefined;
		}
	}
	return madeChange
}

btnApply.onclick = () => {
	try {
		applyConfigChange();
		putAsync("config", config)
			.then((e) => {
				switch (e.status) {
					case 200:
						setPutState("Successfully Applied Settings", 1000);
						break;
					case 400:
					case 404:
					case 405:
					default:
						console.log(e);
						setPutState("Failed to Apply Settings", 5000);
						break;
				}
			})
	} catch (err) {
		console.error(err);
		setPutState("Failed to Apply Settings", 5000);
	}
};
btnReset.onclick = () => {
	try {
		configUpdate = DefaultConfig;
		if (applyConfigChange()) {
			putAsync("config", config)
				.then((e) => {
					switch (e.status) {
						case 200:
							setPutState("Successfully Reset Settings", 1000);
							break;
						case 400:
						case 404:
						case 405:
						default:
							console.log(e);
							setPutState("Failed to Reset Settings", 5000);
							break;
					}
				})
		}
	} catch (err) {
		console.error(err);
		setPutState("Failed to Reset Settings", 5000);
	}
};
btnCancel.onclick = () => {
	configUpdate = {};
	cbxAutostart.checked = config.autostart;
	if ('cameraID' in config) camSelect.value = config.cameraID;
	else camera.getCameraIDByName(config.cameraName).then((id) => { camSelect.value = id; });
};

btnStart.onclick = () => {
	startAILoop();
};
btnStop.onclick = () => {
	activeState = false;
	//Stop();
};

camera.updateCameraSelector(camSelect);

btnCamRef.onclick = () => {
	btnCamRef.disabled = true;
	let v = camSelect.value;
	camera.updateCameraSelector(camSelect).then(() => {
		camSelect.value = v;
		btnCamRef.disabled = false;
	});
};

camSelect.onchange = () => {
	camera.getCameraNameByID(camSelect.value).then((name) => {
		if (name === "") {
			camera.updateCameraSelector(camSelect);
			camSelect.value = "";
			console.log("Invalid Camera Selected");
		} else {
			configUpdate.cameraName = name;
			configUpdate.cameraID = camSelect.value;
		}
	})
};
cbxAutostart.onchange = () => {
	configUpdate.autostart = cbxAutostart.checked;
};

configSelect.onclick = () => {
	GetConfigs();
}
configSelect.onchange = () => {
	let value = Number(configSelect.value);
	if (value != config.id) {
		SwitchConfig(value);
	}
}

async function drawPose(pose) {
	let ctx = canvas.getContext("2d");
	ctx.clearRect(0, 0, canvas.width, canvas.height);
	Object.keys(pose).forEach((key) => {
		let spl = key.split("_");
		if (spl[0] == "right") ctx.fillStyle = "red";
		else if (spl[0] == "left") ctx.fillStyle = "green";
		else ctx.fillStyle = "blue";
		let point = pose[key];
		ctx.beginPath();
		ctx.arc(point.x, point.y, 5, 0, 2 * Math.PI);
		ctx.fill();
	});
}

function debounce(func, wait, immediate) {
	var timeout;
	return function () {
		var context = this, args = arguments;
		var later = function () {
			timeout = null;
			if (!immediate) func.apply(context, args);
		};
		var callNow = immediate && !timeout;
		clearTimeout(timeout);
		timeout = setTimeout(later, wait);
		if (callNow) func.apply(context, args);
	};
};

function resizeCanvas() {
	let rect = video.getBoundingClientRect();
	canvas.width = rect.width;
	canvas.height = rect.height;
	if (poseDetector) poseDetector.width = rect.width;
}
resizeCanvas();

window.addEventListener("resize", debounce(resizeCanvas, 250, false));

function sleep(ms) {
	return new Promise(resolve => setTimeout(resolve, ms));
}

async function sendPose(pose) {
	await putAsync("poseData", {
		"id": config.id,
		"pose": pose
	});
}
async function sendSize() {
	let rect = video.getBoundingClientRect();
	await putAsync("cameraSize", {
		"id": config.id,
		"width": rect.width,
		"height": rect.height
	});
}
async function sendStart() {
	let rect = video.getBoundingClientRect();
	await putAsyncText("start", config.id);
}
async function sendConnect() {
	let rect = video.getBoundingClientRect();
	await putAsyncText("connect", config.id);
}

async function AILoop() {
	let pose = await poseDetector.getFilteredPose(video, config.confidenceThreshold);
	await sendPose(pose);
	drawPose(pose);
}

async function startAILoop() {
	try {
		activeState = true;

		if (!('cameraID' in config) || config.cameraID == "") config.cameraID = await camera.getCameraIDByName(config.cameraName);
		video.srcObject = await camera.getCameraStream(config.cameraID);
		
		if (!poseDetector.detector) await poseDetector.createDetector();

		resizeCanvas();
		canvas.classList.remove("d-none");
		let start, end, delta;

		/*poseDetector.estimatePose(video).then((data) => {
			console.log(data[0].keypoints.map((d) => {
				return d.name;
			}))});*/
		sendConnect();
		sendSize();

		lblState.innerHTML = "Started Successfully"

		await AILoop();
		sendStart();

		while (activeState) {
			start = (performance || Date).now();
			await AILoop();
			end = (performance || Date).now();
			delta = end - start;
			if (delta < 16.66) {
				await sleep(16.66 - delta);
			}
		}
	} catch (err) {
		console.error(err);
		activeState = false;
		lblState.innerHTML = "Failed To Start..."
	}
}

async function GetConfigs() {
	var response;
	try {
		response = await fetch("config.json");
		let data = await response.json();
		let configs = data.windowConfigs;
		//console.log(configs);
		numConfigs = configs.length;
		configSelect.innerHTML = "<option value=-1>Select:</option>\n<option value=-2>Create New</option>";
		for (let i = 0; i < numConfigs; i++) {
			configSelect.innerHTML += `\n<option value=${i}>${i}</option>`;
		}
	} catch (err) {
		console.error(err);
		return;
	}
}
async function SwitchConfig(fetchID) {
	var response;
	try {
		response = await putAsync("SwitchConfig", {
			now: config.id,
			to: fetchID
		});
	} catch (err) {
		console.error(err);
		return;
	}
	let data = await response.json();
	//if confirmed, getConfig
	lblState.innerHTML = "Loaded Config, reading...";
	data.status = null;
	config = data;
	if (config.id >= numConfigs) {
		for (let i = numConfigs; i <= config.id; i++) {
			configSelect.innerHTML += `\n<option value=${i}>${i}</option>`;
		}
	}
	configSelect.value = config.id;
	let camid = "";
	if ('cameraID' in data) camid = data.cameraID
	else camID = await camera.getCameraIDByName(data.cameraName);
	camSelect.value = camid;
	//camSelect.dispatchEvent(new Event('change'));

	cbxAutostart.checked = data.autostart;

	if (data.autostart) {
		lblState.innerHTML = "Autostarting...";
		startAILoop();
	}
	lblState.innerHTML = "Loaded!";
}
async function GetConfig(fetchID) {
	var response;
	try {
		if (fetchID < 0) {
			response = await fetch("config");
		}
		else {
			response = await putAsync("config", fetchID);
		}
	} catch (err) {
		console.error(err);
		return;
	}

	//console.log(response);
	let data = await response.json();
	//console.log(data);
	let status = data.status;
	data.status = null;
	if (status != "ok") {
		console.log(`Error: ${status}`);
		lblState.innerHTML = `Loaded Error/Status:<br>${status}`;
	}
	lblState.innerHTML = "Loaded Config, reading...";
	config = data;
	if (config.id >= numConfigs) {
		for (let i = numConfigs; i <= config.id; i++) {
			configSelect.innerHTML += `\n<option value=${i}>${i}</option>`;
		}
	}
	configSelect.value = config.id;
	let camid = await camera.getCameraIDByName(data.cameraName);
	camSelect.value = camid;
	//camSelect.dispatchEvent(new Event('change'));

	cbxAutostart.checked = data.autostart;

	if (data.autostart) {
		lblState.innerHTML = "Autostarting...";
		startAILoop();
	}
	lblState.innerHTML = "Loaded!";
	setPutState("Connected To Server", 1000);
	controlPanel.classList.remove("d-none");
}

lblState.innerHTML = "<i>Getting Config...</i>";
GetConfigs();
GetConfig(-1);