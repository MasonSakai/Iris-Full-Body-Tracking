export const DefaultConfig = {
    id: -1,
    cameraName: "",
    cameraID: "",
    autostart: false,
    confidenceThreshold: 0.3,
    flip_horizontal: false
};
export async function fetchAsync(port) {
    let response = await fetch(port);
    let data = await response.json();
    return data;
}
export async function fetchAsyncText(port) {
    let response = await fetch(port);
    let data = await response.text();
    return data;
}
export async function putAsync(port, data) {
    return await fetch(port, {
        method: 'PUT',
        headers: {
            'Content-type': 'application/json'
        },
        body: JSON.stringify(data)
    });
}
export async function putAsyncText(port, data) {
    return await fetch(port, {
        method: 'PUT',
        headers: {
            'Content-type': 'text/text'
        },
        body: data
    });
}
export async function sendPose(id, pose) {
    await putAsync("poseData", {
        id: id,
        pose: pose
    });
}
export async function sendSize(id, video) {
    let rect = video.getBoundingClientRect();
    await putAsync("cameraSize", {
        id: id,
        width: rect.width,
        height: rect.height
    });
}
export async function sendStart(id) {
    await putAsyncText("start", id.toString());
}
export async function sendConnect(id) {
    await putAsyncText("connect", id.toString());
}
export async function PutConfig(config) {
    putAsync("config", config);
}
export async function GetConfigs() {
    try {
        var response = await fetch("config.json");
        let data = await response.json();
        //add fail check
        data = data.windowConfigs;
        for (var i = 0; i < data.length; i++) {
            data[i].id = i;
        }
        return data;
        //console.log(configs);
        //numConfigs = configs.length;
        //configSelect.innerHTML = "<option value=-1>Select:</option>\n<option value=-2>Create New</option>";
        //for (let i = 0; i < numConfigs; i++) {
        //	configSelect.innerHTML += `\n<option value=${i}>${i}</option>`;
        //}
    }
    catch (err) {
        console.error(err);
        return;
    }
}
//# sourceMappingURL=net.js.map