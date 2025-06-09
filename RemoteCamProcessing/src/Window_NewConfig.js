import { Camera } from "./camera-manager";
import { DefaultConfig } from "./util";
import { findBestMatch } from "string-similarity";
var div_window = document.getElementById("Window_NewConfig");
var el_video = div_window.querySelector("video");
var select_config = div_window.querySelector("ul#wnc-ex");
var select_config_btn = select_config.previousElementSibling;
var btn_cancel = div_window.querySelector("button#wnc-cancel");
var btn_new = div_window.querySelector("button#wnc-new");
var txt_name = div_window.querySelector("input#wnc-name");
var cbx_autostart = div_window.querySelector("input#wnc-autostart");
var num_thresh = div_window.querySelector("input#wnc-threshold");
var cbx_flipHorizontal = div_window.querySelector("input#wnc-flipHorizontal");
export function Window_NewConfig(camID, configs) {
    return new Promise(async (resolve, reject) => {
        open(camID);
        var downOn = false;
        div_window.onmousedown = (ev) => {
            downOn = ev.target == div_window;
        };
        div_window.onmouseup = (ev) => {
            if (downOn) {
                if (ev.target == div_window) {
                    close();
                    resolve(undefined);
                }
            }
            downOn = false;
        };
        btn_cancel.onclick = () => {
            close();
            resolve(undefined);
        };
        var camData = await Camera.GetCameraByID(camID);
        await populateSelector(camData, configs, resolve);
        populateNew(camData);
        btn_new.onclick = () => {
            var config = DefaultConfig;
            config.id = configs.length;
            config.cameraID = camID;
            config.cameraName = txt_name.value;
            config.autostart = cbx_autostart.checked;
            config.flip_horizontal = cbx_flipHorizontal.checked;
            config.confidenceThreshold = num_thresh.valueAsNumber;
            close();
            resolve(config);
        };
        txt_name.oninput = () => {
            btn_new.disabled = configs.some(c => c.cameraName == txt_name.value);
        };
    });
}
async function open(camID) {
    div_window.classList.remove("d-none");
    el_video.srcObject = await Camera.GetCameraStream(camID);
    await el_video.play();
}
function close() {
    var mediaStream = el_video.srcObject;
    if (mediaStream) {
        const tracks = mediaStream.getTracks();
        tracks.forEach(track => track.stop());
        el_video.srcObject = null;
    }
    div_window.classList.add("d-none");
    div_window.onkeydown = undefined;
    select_config.onchange = undefined;
}
async function populateSelector(camera, configs, resolve) {
    select_config.innerHTML = "";
    configs = configs.filter(v => document.body.querySelector(`.card[config-id="${v.id}"]`) == undefined);
    var noSelectors = configs == undefined || configs.length == 0;
    select_config_btn.classList.toggle("d-none", noSelectors);
    if (noSelectors)
        return;
    var matches = findBestMatch(Camera.GetMixedName(camera), configs.map(conf => conf.cameraName)).ratings;
    matches.sort((a, b) => b.rating - a.rating);
    var cams = await Camera.GetCameras();
    var indexesUsed = [];
    matches = matches.map(rat => {
        var index = configs.findIndex((conf, ind) => conf.cameraName == rat.target && !indexesUsed.includes(ind));
        indexesUsed.push(index);
        return {
            config: configs[index],
            hasID: cams.some(v => v.id == configs[index].cameraID)
        };
    });
    var seenFound = false;
    var passedFound = false;
    matches
        .sort((a, b) => {
        var va = a.hasID ? 1 : 0;
        var vb = b.hasID ? 1 : 0;
        return va - vb;
    })
        .forEach((v) => {
        if (!v.hasID) {
            seenFound = true;
        }
        else if (seenFound && !passedFound) {
            passedFound = true;
            var li = document.createElement("li");
            var hr = document.createElement("hr");
            hr.className = "dropdown-divider";
            li.appendChild(hr);
            select_config.appendChild(li);
        }
        var li = document.createElement("li");
        var btn = document.createElement("button");
        btn.type = "button";
        btn.className = "dropdown-item";
        btn.innerText = v.config.cameraName;
        btn.onclick = () => {
            v.config.cameraID = camera.id;
            close();
            resolve(v.config);
        };
        li.appendChild(btn);
        select_config.appendChild(li);
    });
}
function populateNew(camera) {
    txt_name.value = Camera.GetMixedName(camera);
    cbx_autostart.checked = DefaultConfig.autostart;
    num_thresh.valueAsNumber = DefaultConfig.confidenceThreshold;
    cbx_flipHorizontal.checked = DefaultConfig.flip_horizontal;
}
//# sourceMappingURL=Window_NewConfig.js.map