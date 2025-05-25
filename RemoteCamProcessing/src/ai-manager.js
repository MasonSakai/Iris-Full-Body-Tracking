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
exports.PoseDetectorFactory = void 0;
exports.GetFilteredPose = GetFilteredPose;
require("@tensorflow/tfjs-backend-webgl");
require("@tensorflow/tfjs-backend-webgpu");
var tf = require("@tensorflow/tfjs-core");
var posedetection = require("@tensorflow-models/pose-detection");
var PoseDetectorFactory = /** @class */ (function () {
    function PoseDetectorFactory(width, backend) {
        if (width === void 0) { width = 640; }
        if (backend === void 0) { backend = "webgpu"; }
        tf.setBackend("webgpu");
        this.width = width;
    }
    PoseDetectorFactory.prototype.createDetector = function () {
        return __awaiter(this, arguments, void 0, function (model_type) {
            var modelType;
            if (model_type === void 0) { model_type = "SINGLEPOSE_THUNDER"; }
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0: return [4 /*yield*/, tf.ready()];
                    case 1:
                        _a.sent();
                        modelType = posedetection.movenet.modelType[model_type];
                        return [4 /*yield*/, posedetection.createDetector(posedetection.SupportedModels.MoveNet, { modelType: modelType })];
                    case 2: return [2 /*return*/, _a.sent()];
                }
            });
        });
    };
    return PoseDetectorFactory;
}());
exports.PoseDetectorFactory = PoseDetectorFactory;
function GetFilteredPose(video_1, detector_1) {
    return __awaiter(this, arguments, void 0, function (video, detector, threshold, flipHorizontal, maxPoses) {
        var raw, poses, _loop_1, _i, raw_1, p;
        if (threshold === void 0) { threshold = 0.3; }
        if (flipHorizontal === void 0) { flipHorizontal = false; }
        if (maxPoses === void 0) { maxPoses = 1; }
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0: return [4 /*yield*/, detector.estimatePoses(video, { maxPoses: maxPoses, flipHorizontal: flipHorizontal })];
                case 1:
                    raw = _a.sent();
                    poses = [];
                    _loop_1 = function () {
                        var keypoints = p.keypoints;
                        var filtered = keypoints.filter(function (data) {
                            return data.score >= threshold;
                        });
                        var pose = {};
                        filtered.forEach(function (data) {
                            pose[data.name] = {
                                x: data.x,
                                y: data.y,
                                score: data.score
                            };
                        });
                        poses.push(pose);
                    };
                    for (_i = 0, raw_1 = raw; _i < raw_1.length; _i++) {
                        p = raw_1[_i];
                        _loop_1();
                    }
                    return [2 /*return*/, poses];
            }
        });
    });
}
//# sourceMappingURL=ai-manager.js.map