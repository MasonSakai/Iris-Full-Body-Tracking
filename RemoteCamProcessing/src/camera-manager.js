export class Camera {
    el_div;
    el_canvas;
    el_video;
    span_fps;
    deviceID;
    flip_horizontal = false;
    threshold = 0.3;
    ai_worker;
    ctx;
    constructor(deviceID) {
        this.deviceID = deviceID;
    }
    createElement(videoReadyCallback = undefined) {
        this.el_div = document.createElement("div");
        this.el_div.id = this.deviceID;
        this.el_div.className = "camera-card";
        var div_label = document.createElement("div");
        div_label.className = "camera-label";
        Camera.GetCameraByID(this.deviceID).then(v => div_label.innerText = v == undefined ? "ERROR GETTING NAME" : Camera.GetMixedName(v));
        this.el_div.appendChild(div_label);
        var div_camera = document.createElement("div");
        div_camera.className = "camera-display";
        this.el_video = document.createElement("video");
        Camera.GetCameraStream(this.deviceID)
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
        this.el_div.appendChild(div_camera);
        var div_controls = document.createElement("div");
        div_controls.classList = "camera-controls";
        this.span_fps = document.createElement("span");
        this.span_fps.classList = "fps";
        div_controls.appendChild(this.span_fps);
        this.el_div.appendChild(div_controls);
        return this.el_div;
    }
    processPose(canvas, ctx) {
        canvas.width = this.el_video.videoWidth;
        canvas.height = this.el_video.videoHeight;
        ctx.drawImage(this.el_video, 0, 0, this.el_video.videoWidth, this.el_video.videoHeight);
        this.ai_worker.postMessage({
            type: "video",
            image: ctx.getImageData(0, 0, this.el_video.videoWidth, this.el_video.videoHeight)
        });
    }
    startWorker() {
        if (typeof (Worker) === "undefined") {
            Camera.GetCameraByID(this.deviceID).then(v => {
                console.log(`Camera worker ${Camera.GetMixedName(v)} failed`);
            });
            return;
        }
        this.ai_worker = new Worker("CameraWorker.js", { type: "module" });
        this.ai_worker.onmessage = async (ev) => {
            var data = ev.data;
            switch (data.type) {
                case "debug":
                    console.log(`Camera worker ${Camera.GetMixedName(await Camera.GetCameraByID(this.deviceID))}`, data.message);
                    break;
                case "error":
                    console.error(`Camera worker ${Camera.GetMixedName(await Camera.GetCameraByID(this.deviceID))} error`, data.error);
                    break;
                case "pose":
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
            }
        };
        this.ai_worker.onerror = async (ev) => {
            console.log(`Camera worker ${Camera.GetMixedName(await Camera.GetCameraByID(this.deviceID))} onerror`, ev);
        };
        this.ai_worker.onmessageerror = async (ev) => {
            console.log(`Camera worker ${Camera.GetMixedName(await Camera.GetCameraByID(this.deviceID))} onmessageerror`, ev);
        };
        this.ai_worker.postMessage({ type: "config", flip_horizontal: this.flip_horizontal, threshold: this.threshold });
        this.ai_worker.postMessage({ type: "start" });
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
    static async UpdateCameraSelector(camSelect) {
        let cameras = await Camera.GetCameras();
        if (cameras == undefined)
            return;
        cameras = cameras.filter(v => document.getElementById(v.id) == undefined);
        camSelect.innerHTML = `<option value="">Select camera</option>`;
        cameras.forEach((camera) => {
            camSelect.innerHTML += `\n<option value=${camera.id}>${Camera.GetMixedName(camera)}</option>`;
        });
    }
    static GetMixedName(info) {
        return `${info.label.split(" (")[0]} (${info.id.substring(0, 6)})`;
    }
}
//# sourceMappingURL=camera-manager.js.map