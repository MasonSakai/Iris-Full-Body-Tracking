"use strict";
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __generator = (this && this.__generator) || function (thisArg, body) {
    var _ = { label: 0, sent: function() { if (t[0] & 1) throw t[1]; return t[1]; }, trys: [], ops: [] }, f, y, t, g = Object.create((typeof Iterator === "function" ? Iterator : Object).prototype);
    return g.next = verb(0), g["throw"] = verb(1), g["return"] = verb(2), typeof Symbol === "function" && (g[Symbol.iterator] = function() { return this; }), g;
    function verb(n) { return function (v) { return step([n, v]); }; }
    function step(op) {
        if (f) throw new TypeError("Generator is already executing.");
        while (g && (g = 0, op[0] && (_ = 0)), _) try {
            if (f = 1, y && (t = op[0] & 2 ? y["return"] : op[0] ? y["throw"] || ((t = y["return"]) && t.call(y), 0) : y.next) && !(t = t.call(y, op[1])).done) return t;
            if (y = 0, t) op = [op[0] & 2, t.value];
            switch (op[0]) {
                case 0: case 1: t = op; break;
                case 4: _.label++; return { value: op[1], done: false };
                case 5: _.label++; y = op[1]; op = [0]; continue;
                case 7: op = _.ops.pop(); _.trys.pop(); continue;
                default:
                    if (!(t = _.trys, t = t.length > 0 && t[t.length - 1]) && (op[0] === 6 || op[0] === 2)) { _ = 0; continue; }
                    if (op[0] === 3 && (!t || (op[1] > t[0] && op[1] < t[3]))) { _.label = op[1]; break; }
                    if (op[0] === 6 && _.label < t[1]) { _.label = t[1]; t = op; break; }
                    if (t && _.label < t[2]) { _.label = t[2]; _.ops.push(op); break; }
                    if (t[2]) _.ops.pop();
                    _.trys.pop(); continue;
            }
            op = body.call(thisArg, _);
        } catch (e) { op = [6, e]; y = 0; } finally { f = t = 0; }
        if (op[0] & 5) throw op[1]; return { value: op[0] ? op[1] : void 0, done: true };
    }
};
Object.defineProperty(exports, "__esModule", { value: true });
var camera_manager_1 = require("./camera-manager");
var ai_manager_1 = require("./ai-manager");
var span_fps = document.getElementById("fps");
var div_cameras = document.getElementById("camera-display");
var select_camera = document.getElementById("camera-select");
var poseDetector = new ai_manager_1.PoseDetectorFactory();
var cameras = [];
camera_manager_1.Camera.UpdateCameraSelector(select_camera);
/*Camera.GetCameras()
    .then(vals => {
        for (var val of vals) {
            var camera = new Camera(val.id)
            div_cameras.appendChild(camera.createElement())

            //await new Promise(resolve => setTimeout(resolve, 2000))

            //var context = camera.el_canvas.getContext("2d")
            //context.drawImage(camera.el_video, 0, 0, camera.el_canvas.width, camera.el_canvas.height)
            //console.log({ w: camera.el_canvas.width, h: camera.el_canvas.height })

            //window.location.href = camera.el_canvas.toDataURL("image/png").replace("image/png", "image/octet-stream")

            //await new Promise(resolve => setTimeout(resolve, 500))
            //context.clearRect(0, 0, camera.el_canvas.width, camera.el_canvas.height)

        }
        Camera.UpdateCameraSelector(select_camera)
})*/
var draw = false;
select_camera.onchange = function () {
    if (select_camera.value == "")
        return;
    poseDetector.createDetector()
        .then(function (detector) {
        var camera = new camera_manager_1.Camera(select_camera.value);
        camera.detector = detector;
        div_cameras.appendChild(camera.createElement(function () {
            cameras.push(camera);
            draw = true;
            //setInterval(() => {
            //	var context = camera.el_canvas.getContext("2d")
            //	context.drawImage(camera.el_video, 0, 0, camera.el_canvas.width, camera.el_canvas.height)
            //	console.log({ w: camera.el_canvas.width, h: camera.el_canvas.height })
            //	window.location.href = camera.el_canvas.toDataURL("image/png").replace("image/png", "image/octet-stream")
            //}, 5000)
        }));
        select_camera.value = "";
        camera_manager_1.Camera.UpdateCameraSelector(select_camera);
    });
};
function AILoop() {
    return __awaiter(this, void 0, void 0, function () {
        var start, end, delta, _i, cameras_1, camera;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0:
                    if (!true) return [3 /*break*/, 7];
                    start = (performance || Date).now();
                    if (!draw) return [3 /*break*/, 4];
                    _i = 0, cameras_1 = cameras;
                    _a.label = 1;
                case 1:
                    if (!(_i < cameras_1.length)) return [3 /*break*/, 4];
                    camera = cameras_1[_i];
                    return [4 /*yield*/, camera.processPose(poseDetector)];
                case 2:
                    _a.sent();
                    _a.label = 3;
                case 3:
                    _i++;
                    return [3 /*break*/, 1];
                case 4:
                    end = (performance || Date).now();
                    delta = end - start;
                    span_fps.innerText = delta.toString().substr(0, 4);
                    if (!(delta < 16.66)) return [3 /*break*/, 6];
                    return [4 /*yield*/, sleep(16.66 - delta)];
                case 5:
                    _a.sent();
                    _a.label = 6;
                case 6: return [3 /*break*/, 0];
                case 7: return [2 /*return*/];
            }
        });
    });
}
AILoop();
function sleep(ms) {
    return new Promise(function (resolve) { return setTimeout(resolve, ms); });
}
/*
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
            }))});* /
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
GetConfig(-1);*/ 
//# sourceMappingURL=index.js.map