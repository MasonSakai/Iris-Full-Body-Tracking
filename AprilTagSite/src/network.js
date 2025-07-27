import * as THREE from 'three';
import { createMatrixT } from './util';
import { PickHelper } from './PickHelper';
import './ui';
import { scene, LookAt } from './apriltag3D';
import { io } from 'socket.io-client';
let texLoader = new THREE.TextureLoader();
export let socket = io('/apriltag');
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
    if (ident in known_tag_list) {
        selected = known_tag_list[ident];
        selected.el.classList.toggle('active', true);
        LookAt(selected.obj);
    }
    selectionChange_listeners.forEach(f => f(event));
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
    selectionChange_listeners.forEach(f => f(event));
}
PickHelper.add_default_listener(on_tag_select);
export let known_tag_list = {};
export let camera_list = {};
export let selected = null;
export let selectionChange_listeners = [];
export let refresh_listeners = [];
async function ParseFoundTags(data) {
    //var el_tags_found = document.getElementById('tags-found').nextSibling
    //for (const ident in tag_list) {
    //	if (!tag_list[ident].known) {
    //		tag_list[ident].el.remove()
    //		PickHelper.removeListeners(tag_list[ident].obj)
    //		tag_list[ident].obj.removeFromParent()
    //		delete tag_list[ident]
    //	}
    //}
    //for (const ident in data) {
    //	var size = data[ident].size
    //	var model = await LoadTagModel(ident, size)
    //	model.visible = false
    //	model.name = ident
    //	scene.add(model)
    //	var el = document.createElement('button')
    //	el.className = 'list-group-item list-group-item-action d-flex justify-content-between align-items-center'
    //	el.innerText = ident
    //	el.id = ident
    //	var num = document.createElement('span')
    //	num.className = 'badge rounded-pill'
    //	num.classList.add('text-bg-warning')
    //	num.innerText = data[ident].cams.length
    //	el.appendChild(num)
    //	el_tags_found.parentElement.insertBefore(el, el_tags_found)
    //	PickHelper.addListener(model, (event, m) => {
    //		on_tag_select(event, m.name)
    //	})
    //	el.onclick = (event) => {
    //		on_tag_select(event, (event.target as HTMLButtonElement).id)
    //	}
    //	tag_list[ident] = {
    //		known: false,
    //		obj: model,
    //		el: el,
    //		transform: null,
    //		static: false,
    //		cams: data[ident].cams,
    //		ident: ident
    //	}
    //}
    on_refresh();
}
socket.on('found_tags', ParseFoundTags);
async function ParseKnownTags(data) {
    var el_tags_known = document.getElementById('tags-known').nextSibling;
    //for (const ident in known_tag_list) {
    //	known_tag_list[ident].el.remove()
    //	PickHelper.removeListeners(known_tag_list[ident].obj)
    //	known_tag_list[ident].obj.removeFromParent()
    //	delete known_tag_list[ident]
    //}
    for (const i in data) {
        var tag = data[i].tag;
        var trans = tag.transform.length > 0 ? createMatrixT(tag.transform) : null;
        if (!(tag.ident in known_tag_list)) {
            var model = await LoadTagModel(tag.ident, tag.size);
            model.name = tag.ident;
            scene.add(model);
            var el = document.createElement('button');
            el.className = 'list-group-item list-group-item-action d-flex justify-content-between align-items-center';
            el.id = tag.ident;
            el_tags_known.parentElement.insertBefore(el, el_tags_known);
            PickHelper.addListener(model, (event, m) => {
                on_tag_select(event, m.name);
            });
            el.onclick = (event) => {
                on_tag_select(event, event.target.id);
            };
            known_tag_list[tag.ident] = {
                obj: model,
                el: el,
                transform: trans,
                static: tag.static,
                cams: data[i].cams,
                ident: tag.ident
            };
        }
        known_tag_list[tag.ident].el.innerText = tag.name;
        var num = document.createElement('span');
        num.className = 'badge rounded-pill';
        num.classList.add(trans == null ? 'text-bg-warning' : tag.static ? 'text-bg-primary' : 'text-bg-secondary');
        num.innerText = data[i].cams.length.toString();
        known_tag_list[tag.ident].el.appendChild(num);
        known_tag_list[tag.ident].transform = trans;
        known_tag_list[tag.ident].obj.visible = trans != null;
        if (trans != null)
            trans.decompose(known_tag_list[tag.ident].obj.position, known_tag_list[tag.ident].obj.quaternion, known_tag_list[tag.ident].obj.scale);
    }
    on_refresh();
}
socket.on('tags', ParseKnownTags);
async function ParseCameras(data) {
    var el_cams = document.getElementById('cameras').nextSibling;
    //for (const ident in camera_list) {
    //	camera_list[ident].el.remove()
    //	PickHelper.removeListeners(camera_list[ident].obj)
    //	camera_list[ident].obj.removeFromParent()
    //	delete camera_list[ident]
    //}
    var m = await LoadCamModel();
    for (const i in data) {
        var cam = data[i];
        var trans = cam.transform.length > 0 ? createMatrixT(cam.transform) : null;
        if (!(cam.id in camera_list)) {
            var model = m.clone();
            model.name = cam.id;
            model.visible = trans != null;
            if (trans != null)
                trans.decompose(model.position, model.quaternion, model.scale);
            scene.add(model);
            var el = document.createElement('button');
            el.className = 'list-group-item list-group-item-action d-flex justify-content-between align-items-center';
            el.id = `cam${cam.id}`;
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
        camera_list[cam.id].el.innerText = cam.name;
        var num = document.createElement('span');
        num.className = 'badge rounded-pill';
        num.classList.add(trans == null ? 'text-bg-warning' : 'text-bg-secondary');
        num.innerText = '-1';
        camera_list[cam.id].el.appendChild(num);
        camera_list[cam.id].transform = trans;
        camera_list[cam.id].obj.visible = trans != null;
        if (trans != null)
            trans.decompose(camera_list[cam.id].obj.position, camera_list[cam.id].obj.quaternion, camera_list[cam.id].obj.scale);
    }
    on_refresh();
}
socket.on('cams', ParseCameras);
var refreshTimeout = null;
function ResetRefreshTimeout() {
    if (refreshTimeout != null)
        clearTimeout(refreshTimeout);
    refreshTimeout = setTimeout(Refresh, 5000);
}
function on_refresh() {
    ResetRefreshTimeout();
    refresh_listeners.forEach(f => f());
}
export function Refresh() {
    ResetRefreshTimeout();
    socket.emit('tags');
    socket.emit('found_tags');
    socket.emit('cams');
}
//# sourceMappingURL=network.js.map