import { IrisSocket_Key } from "./IrisWebClient_keys";
import { PutConfig, GetConfigs, CreateCheckbox, CreateRange } from "./util";
export class Camera {
    el_card;
    el_canvas;
    el_video;
    span_fps;
    config;
    ai_worker;
    ctx;
    constructor(config) {
        this.config = config;
    }
    createElement(videoReadyCallback = undefined) {
        this.el_card = document.createElement("div");
        this.el_card.setAttribute("config-id", this.config.id.toString());
        this.el_card.setAttribute("camera-id", this.config.cameraID);
        this.el_card.className = "card bg-body-secondary border border-secondary-subtle";
        var div_label = document.createElement("div");
        div_label.className = "card-header input-group";
        var span_label = document.createElement("span");
        span_label.className = "input-group-text";
        span_label.innerText = this.config.cameraName;
        div_label.appendChild(span_label);
        var btn_label = document.createElement("button");
        btn_label.className = "btn btn-outline-secondary";
        btn_label.type = "button";
        btn_label.innerHTML = "<i class=\"bi bi-pencil-square\"></i>";
        div_label.appendChild(btn_label);
        btn_label.onclick = () => {
            var name = prompt("Rename camera", this.config.cameraName);
            if (name == null || name === "")
                return;
            if (name == this.config.cameraName)
                return;
            this.config.cameraName = name;
            span_label.innerText = name;
            this.updateConfig();
        };
        this.el_card.appendChild(div_label);
        var div_body = document.createElement("div");
        div_body.className = "card-body";
        var div_camera = document.createElement("div");
        this.el_video = document.createElement("video");
        Camera.GetCameraStream(this.config.cameraID)
            .then(stream => {
            this.el_video.srcObject = stream;
            this.el_video.play()
                .then(() => {
                this.el_canvas.width = this.el_video.videoWidth;
                this.el_canvas.height = this.el_video.videoHeight;
                if (videoReadyCallback != undefined)
                    videoReadyCallback(this);
            });
        });
        div_camera.appendChild(this.el_video);
        this.el_canvas = document.createElement("canvas");
        this.ctx = this.el_canvas.getContext("2d");
        div_camera.appendChild(this.el_canvas);
        div_body.appendChild(div_camera);
        this.el_card.appendChild(div_body);
        var div_footer = document.createElement("div");
        div_footer.classList = "card-footer container-fluid";
        var div_controls = document.createElement("div");
        div_controls.classList = "row";
        var [div_autostart, cbx_autostart] = CreateCheckbox(this.config.id + "-autostart", "Auto-start");
        div_autostart.classList.add("col-auto");
        cbx_autostart.checked = this.config.autostart;
        cbx_autostart.onchange = () => {
            this.config.autostart = cbx_autostart.checked;
            this.updateConfig();
        };
        div_controls.appendChild(div_autostart);
        var [div_flipHorizontal, cbx_flipHorizontal] = CreateCheckbox(this.config.id + "-flipHorizontal", "Flip Horizontal");
        div_flipHorizontal.classList.add("col-auto");
        cbx_flipHorizontal.checked = this.config.flip_horizontal;
        cbx_flipHorizontal.onchange = () => {
            this.config.flip_horizontal = cbx_flipHorizontal.checked;
            this.updateConfig();
        };
        div_controls.appendChild(div_flipHorizontal);
        var [lbl_threshold, range_threshold] = CreateRange(this.config.id + "-threshold", "Threshold");
        lbl_threshold.classList.add("col-auto");
        range_threshold.classList.add("col");
        range_threshold.min = "0";
        range_threshold.max = "1";
        range_threshold.step = "0.01";
        range_threshold.valueAsNumber = this.config.confidenceThreshold;
        range_threshold.setAttribute("list", "threshold-ticks");
        range_threshold.oninput = () => {
            this.config.confidenceThreshold = range_threshold.valueAsNumber;
            this.ai_worker.postMessage({ key: IrisSocket_Key.msg_config, config: this.config });
        };
        range_threshold.onchange = () => {
            this.config.confidenceThreshold = range_threshold.valueAsNumber;
            this.updateConfig();
        };
        div_controls.appendChild(lbl_threshold);
        div_controls.appendChild(range_threshold);
        var div_spacer = document.createElement("div");
        div_spacer.className = "col-auto";
        div_controls.appendChild(div_spacer);
        this.span_fps = document.createElement("div");
        this.span_fps.classList = "col-auto text-body-secondary fps";
        this.span_fps.innerText = "Starting...";
        div_controls.appendChild(this.span_fps);
        div_footer.appendChild(div_controls);
        this.el_card.appendChild(div_footer);
        return this.el_card;
    }
    processImage(canvas, ctx) {
        canvas.width = this.el_video.videoWidth;
        canvas.height = this.el_video.videoHeight;
        ctx.drawImage(this.el_video, 0, 0, this.el_video.videoWidth, this.el_video.videoHeight);
        this.ai_worker.postMessage({
            key: IrisSocket_Key.msg_image,
            image: ctx.getImageData(0, 0, this.el_video.videoWidth, this.el_video.videoHeight)
        });
    }
    updateConfig() {
        this.ai_worker.postMessage({ key: IrisSocket_Key.msg_config, config: this.config });
        PutConfig(this.config);
    }
    startWorker() {
        if (typeof (Worker) === "undefined") {
            console.log(`Camera worker ${this.config.cameraName} failed`);
            return;
        }
        this.ai_worker = new Worker("CameraWorker.js", { type: "module" });
        this.ai_worker.onmessage = (ev) => {
            var data = ev.data;
            switch (data.key) {
                case IrisSocket_Key.msg_pose:
                    this.span_fps.innerText = `${Math.floor(1000 / data.delta)}fps (${data.delta.toFixed(1)}ms)`;
                    this.ctx.clearRect(0, 0, this.el_canvas.width, this.el_canvas.height);
                    this.ctx.strokeStyle = 'White';
                    this.ctx.lineWidth = 1;
                    for (var pose of data.pose) {
                        for (var key in pose) {
                            let spl = key.split("_");
                            if (spl[0] == "right")
                                this.ctx.fillStyle = "red";
                            else if (spl[0] == "left")
                                this.ctx.fillStyle = "green";
                            else
                                this.ctx.fillStyle = "blue";
                            let point = pose[key];
                            const circle = new Path2D();
                            circle.arc(point.x, point.y, 5, 0, 2 * Math.PI);
                            this.ctx.fill(circle);
                            this.ctx.stroke(circle);
                        }
                    }
                    break;
                case IrisSocket_Key.msg_debug:
                    console.log(`Camera worker ${this.config.cameraName}`, data.message);
                    break;
                case IrisSocket_Key.msg_error:
                    console.error(`Camera worker ${this.config.cameraName} error`, data.error);
                    break;
                default:
                    console.log(`Camera worker ${this.config.cameraName} - ${data.key}`, data);
                    break;
            }
        };
        this.ai_worker.onerror = (ev) => {
            console.log(`Camera worker ${this.config.cameraName} onerror`, ev);
        };
        this.ai_worker.onmessageerror = (ev) => {
            console.log(`Camera worker ${this.config.cameraName} onmessageerror`, ev);
        };
        this.ai_worker.postMessage({ key: IrisSocket_Key.msg_config, config: this.config });
        this.ai_worker.postMessage({ key: IrisSocket_Key.msg_start });
    }
    close() {
        this.ai_worker.terminate();
        this.ai_worker = undefined;
    }
    static async GetCameraStream(deviceID = "") {
        if ('mediaDevices' in navigator && 'getUserMedia' in navigator.mediaDevices) {
            let properties = {
                video: {} /*{
                    width: {
                        ideal: 640
                    },
                    height: {
                        ideal: 480
                    }
                }*/
            };
            if (deviceID)
                properties.video["deviceId"] = { exact: deviceID };
            return await navigator.mediaDevices.getUserMedia(properties);
        }
        return undefined;
    }
    static async GetCamerasByName(deviceName) {
        var cameras = await Camera.GetCameras();
        if (!cameras)
            return undefined;
        return cameras.filter(v => v.label == deviceName);
    }
    static async GetCameraByID(deviceID) {
        var cameras = await Camera.GetCameras();
        if (cameras == undefined)
            return undefined;
        return cameras.find(v => v.id == deviceID);
    }
    static async GetCameras() {
        if (!('mediaDevices' in navigator && 'getUserMedia' in navigator.mediaDevices))
            return undefined;
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
    static CameraSelectorCallback = undefined;
    static async UpdateCameraSelector(camSelect, configs = undefined) {
        let cameras = await Camera.GetCameras();
        if (cameras == undefined)
            return;
        if (configs == undefined)
            configs = await GetConfigs();
        var passedConfigs = false;
        var seenConfigs = false;
        camSelect.innerHTML = "";
        cameras
            .filter(v => document.body.querySelector(`.card[camera-id="${v.id}"]`) == undefined)
            .sort((a, b) => {
            var va = configs.find(v => v.cameraID == a.id) != undefined ? 1 : 0;
            var vb = configs.find(v => v.cameraID == b.id) != undefined ? 1 : 0;
            return vb - va;
        })
            .forEach((camera) => {
            var name = Camera.GetMixedName(camera);
            var config = configs.find(v => v.cameraID == camera.id);
            if (config != undefined) {
                name = config.cameraName;
                seenConfigs = true;
            }
            else if (seenConfigs && !passedConfigs) {
                passedConfigs = true;
                var li = document.createElement("li");
                var hr = document.createElement("hr");
                hr.className = "dropdown-divider";
                li.appendChild(hr);
                camSelect.appendChild(li);
            }
            var li = document.createElement("li");
            var btn = document.createElement("button");
            btn.className = "dropdown-item";
            btn.type = "button";
            btn.innerText = name;
            btn.onclick = () => {
                if (this.CameraSelectorCallback)
                    this.CameraSelectorCallback(camera.id);
            };
            li.appendChild(btn);
            camSelect.appendChild(li);
        });
        return cameras;
    }
    static GetMixedName(info) {
        return `${info.label.split(" (")[0]} (${info.id.substring(0, 6)})`;
    }
}
//# sourceMappingURL=camera-manager.js.map