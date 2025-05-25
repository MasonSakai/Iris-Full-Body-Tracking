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
exports.Camera = void 0;
var Camera = /** @class */ (function () {
    function Camera(deviceID) {
        this.flip_horizontal = false;
        this.deviceID = deviceID;
    }
    Camera.prototype.createElement = function (videoReadyCallback) {
        var _this = this;
        if (videoReadyCallback === void 0) { videoReadyCallback = undefined; }
        this.el_div = document.createElement("div");
        this.el_div.id = this.deviceID;
        this.el_div.className = "camera-card";
        var div_label = document.createElement("div");
        div_label.className = "camera-label";
        Camera.GetCameraByID(this.deviceID).then(function (v) {
            return div_label.innerText = v == undefined ? "ERROR GETTING NAME" : Camera.GetMixedName(v);
        });
        this.el_div.appendChild(div_label);
        var div_camera = document.createElement("div");
        div_camera.className = "camera-display";
        this.el_canvas = document.createElement("canvas");
        div_camera.appendChild(this.el_canvas);
        this.el_div.appendChild(div_camera);
        this.el_video = document.createElement("video");
        Camera.GetCameraStream(this.deviceID)
            .then(function (stream) {
            _this.el_video.srcObject = stream;
            _this.el_video.play()
                .then(function () {
                _this.el_canvas.width = _this.el_video.videoWidth;
                _this.el_canvas.height = _this.el_video.videoHeight;
                if (videoReadyCallback != undefined)
                    videoReadyCallback(_this);
            });
        });
        div_camera.appendChild(this.el_video);
        var div_controls = document.createElement("div");
        div_controls.classList = "camera-controls";
        div_controls.innerText = "a";
        this.el_div.appendChild(div_controls);
        return this.el_div;
    };
    Camera.GetCameraStream = function () {
        return __awaiter(this, arguments, void 0, function (deviceID) {
            var properties;
            if (deviceID === void 0) { deviceID = ""; }
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        if (!('mediaDevices' in navigator && 'getUserMedia' in navigator.mediaDevices)) return [3 /*break*/, 2];
                        properties = {
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
                        return [4 /*yield*/, navigator.mediaDevices.getUserMedia(properties)];
                    case 1: return [2 /*return*/, _a.sent()];
                    case 2: return [2 /*return*/, undefined];
                }
            });
        });
    };
    Camera.GetCamerasByName = function (deviceName) {
        return __awaiter(this, void 0, void 0, function () {
            var cameras;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0: return [4 /*yield*/, Camera.GetCameras()];
                    case 1:
                        cameras = _a.sent();
                        if (!cameras)
                            return [2 /*return*/, undefined];
                        return [2 /*return*/, cameras.filter(function (v) { return v.label == deviceName; })];
                }
            });
        });
    };
    Camera.GetCameraByID = function (deviceID) {
        return __awaiter(this, void 0, void 0, function () {
            var cameras;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0: return [4 /*yield*/, Camera.GetCameras()];
                    case 1:
                        cameras = _a.sent();
                        if (cameras == undefined)
                            return [2 /*return*/, undefined];
                        return [2 /*return*/, cameras.find(function (v) { return v.id == deviceID; })];
                }
            });
        });
    };
    Camera.GetCameras = function () {
        return __awaiter(this, void 0, void 0, function () {
            var devices, videoDevices;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        if (!('mediaDevices' in navigator && 'getUserMedia' in navigator.mediaDevices))
                            return [2 /*return*/, undefined];
                        return [4 /*yield*/, navigator.mediaDevices.enumerateDevices()];
                    case 1:
                        devices = _a.sent();
                        videoDevices = devices.filter(function (device) { return device.kind === 'videoinput'; });
                        if (!(videoDevices[0].deviceId == '')) return [3 /*break*/, 4];
                        return [4 /*yield*/, Camera.GetCameraStream()];
                    case 2:
                        _a.sent();
                        return [4 /*yield*/, Camera.GetCameras()];
                    case 3: return [2 /*return*/, _a.sent()];
                    case 4: return [2 /*return*/, videoDevices.map(function (videoDevice) {
                            return {
                                label: videoDevice.label,
                                id: videoDevice.deviceId
                            };
                        })];
                }
            });
        });
    };
    Camera.UpdateCameraSelector = function (camSelect) {
        return __awaiter(this, void 0, void 0, function () {
            var cameras;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0: return [4 /*yield*/, Camera.GetCameras()];
                    case 1:
                        cameras = _a.sent();
                        if (cameras == undefined)
                            return [2 /*return*/];
                        cameras = cameras.filter(function (v) { return document.getElementById(v.id) == undefined; });
                        camSelect.innerHTML = "<option value=\"\">Select camera</option>";
                        cameras.forEach(function (camera) {
                            camSelect.innerHTML += "\n<option value=".concat(camera.id, ">").concat(Camera.GetMixedName(camera), "</option>");
                        });
                        return [2 /*return*/];
                }
            });
        });
    };
    Camera.GetMixedName = function (info) {
        return "".concat(info.label.split(" (")[0], " (").concat(info.id.substring(0, 6), ")");
    };
    return Camera;
}());
exports.Camera = Camera;
//# sourceMappingURL=camera-manager.js.map