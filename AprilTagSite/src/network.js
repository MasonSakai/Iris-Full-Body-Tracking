import * as THREE from 'three';
import { createMatrixTR, createMatrixT } from './util';
import { PickHelper } from './PickHelper';
import { ApplyConstraints } from './constraints';
import { scene, LookAt } from './apriltag3D';
let texLoader = new THREE.TextureLoader();
export async function LoadTagModel(ident, size = 1) {
    var geom = new THREE.PlaneGeometry(size, size);
    var tex = await texLoader.loadAsync(`tags/image/${ident}.png`);
    tex.magFilter = THREE.NearestFilter;
    var mat = new THREE.MeshBasicMaterial({ map: tex });
    mat.side = THREE.DoubleSide;
    var model = new THREE.Mesh(geom, mat);
    model.add(new THREE.AxesHelper(size));
    return model;
}
export async function LoadCamModel() {
    var geom = new THREE.BoxGeometry(0.2, 0.2, 0.1);
    var mat = new THREE.MeshBasicMaterial({ color: 0xFF0000 });
    var model = new THREE.Mesh(geom, mat);
    model.add(new THREE.AxesHelper(0.3));
    return model;
}
function on_tag_select(event, ident = '') {
    if (selected) {
        selected.el.classList.toggle('active', false);
        selected = null;
    }
    if (ident in tag_list) {
        selected = tag_list[ident];
        selected.el.classList.toggle('active', true);
        LookAt(selected.obj);
    }
}
function on_cam_select(event, id = -1) {
    if (selected) {
        selected.el.classList.toggle('active', false);
        selected = null;
    }
    if (id in camera_list) {
        selected = camera_list[id];
        selected.el.classList.toggle('active', true);
        LookAt(selected.obj);
    }
}
PickHelper.add_default_listener(on_tag_select);
export let tag_list = {};
export let camera_list = {};
export let selected = null;
async function FetchFoundTags() {
    var data = await (await fetch('tags/found/list')).json();
    var el_tags_found = document.getElementById('tags-found').nextSibling;
    for (const ident in tag_list) {
        if (!tag_list[ident].known) {
            tag_list[ident].el.remove();
            PickHelper.removeListeners(tag_list[ident].obj);
            tag_list[ident].obj.removeFromParent();
            delete tag_list[ident];
        }
    }
    for (const ident in data) {
        var size = data[ident].size;
        var cams = data[ident].cams;
        var model = await LoadTagModel(ident, size);
        model.visible = false;
        model.name = ident;
        scene.add(model);
        var cam_data = {};
        for (const i in cams) {
            cam_data[cams[i].cam] = createMatrixTR(cams[i].pose_t, cams[i].pose_r);
        }
        var el = document.createElement('button');
        el.className = 'list-group-item list-group-item-action d-flex justify-content-between align-items-center';
        el.innerText = ident;
        el.id = ident;
        var num = document.createElement('span');
        num.className = 'badge rounded-pill';
        num.classList.add('text-bg-warning');
        num.innerText = cams.length;
        el.appendChild(num);
        el_tags_found.parentElement.insertBefore(el, el_tags_found);
        PickHelper.addListener(model, (event, m) => {
            on_tag_select(event, m.name);
        });
        el.onclick = (event) => {
            on_tag_select(event, event.target.id);
        };
        tag_list[ident] = {
            known: false,
            obj: model,
            el: el,
            transform: null,
            static: false,
            cams: cam_data,
            ident: ident
        };
    }
}
async function FetchKnownTags() {
    var data = await (await fetch('tags/list')).json();
    var el_tags_known = document.getElementById('tags-known').nextSibling;
    for (const ident in tag_list) {
        if (tag_list[ident].known) {
            tag_list[ident].el.remove();
            PickHelper.removeListeners(tag_list[ident].obj);
            tag_list[ident].obj.removeFromParent();
            delete tag_list[ident];
        }
    }
    for (const ent in data) {
        var tag = data[ent].tag;
        var cams = data[ent].cams;
        var cam_data = {};
        for (const i in cams) {
            var cam = cams[i];
            cam_data[cam.cam] = createMatrixTR(cam.pose_t, cam.pose_r);
        }
        var trans = tag.transform.length > 0 ? createMatrixT(tag.transform) : null;
        var model = await LoadTagModel(tag.ident, tag.size);
        model.name = tag.ident;
        model.visible = trans != null;
        if (trans != null)
            trans.decompose(model.position, model.quaternion, model.scale);
        scene.add(model);
        var el = document.createElement('button');
        el.className = 'list-group-item list-group-item-action d-flex justify-content-between align-items-center';
        el.innerText = tag.name;
        el.id = tag.ident;
        var num = document.createElement('span');
        num.className = 'badge rounded-pill';
        num.classList.add(trans == null ? 'text-bg-warning' : tag.static ? 'text-bg-primary' : 'text-bg-secondary');
        num.innerText = cams.length;
        el.appendChild(num);
        el_tags_known.parentElement.insertBefore(el, el_tags_known);
        PickHelper.addListener(model, (event, m) => {
            on_tag_select(event, m.name);
        });
        el.onclick = (event) => {
            on_tag_select(event, event.target.id);
        };
        tag_list[tag.ident] = {
            known: true,
            obj: model,
            el: el,
            transform: trans,
            static: tag.static,
            cams: cam_data,
            ident: tag.ident
        };
    }
}
async function FetchCameras() {
    var data = await (await fetch('cameras/list')).json();
    var el_cams = document.getElementById('cameras').nextSibling;
    for (const ident in camera_list) {
        camera_list[ident].el.remove();
        PickHelper.removeListeners(camera_list[ident].obj);
        camera_list[ident].obj.removeFromParent();
        delete camera_list[ident];
    }
    var m = await LoadCamModel();
    for (const i in data) {
        var cam = data[i];
        var trans = cam.transform.length > 0 ? createMatrixT(cam.transform) : null;
        var model = m.clone();
        model.name = cam.id;
        model.visible = trans != null;
        if (trans != null)
            trans.decompose(model.position, model.quaternion, model.scale);
        scene.add(model);
        var el = document.createElement('button');
        el.className = 'list-group-item list-group-item-action d-flex justify-content-between align-items-center';
        el.innerText = cam.name;
        el.id = `cam${cam.id}`;
        var num = document.createElement('span');
        num.className = 'badge rounded-pill';
        num.classList.add(trans == null ? 'text-bg-warning' : 'text-bg-secondary');
        num.innerText = '-1';
        el.appendChild(num);
        el_cams.parentElement.insertBefore(el, el_cams);
        PickHelper.addListener(model, (event, m) => {
            on_cam_select(event, parseInt(m.name));
        });
        el.onclick = (event) => {
            on_cam_select(event, parseInt(event.target.id.substring(3)));
        };
        camera_list[cam.id] = {
            obj: model,
            el: el,
            transform: trans,
            ident: cam.id
        };
    }
}
export async function Refresh() {
    selected = null;
    await FetchKnownTags();
    await FetchFoundTags();
    await FetchCameras();
    ApplyConstraints();
}
export function DebugPositions() {
    console.log("Debugging positions");
    for (const ident in tag_list) {
        var tag = tag_list[ident];
        var model = tag.obj;
        for (const i in tag.cams) {
            var m = model.clone();
            m.visible = true;
            m.matrixAutoUpdate = false;
            m.matrix.copy(tag.cams[i]);
            scene.add(m);
        }
    }
}
//# sourceMappingURL=network.js.map