import { Matrix4 } from 'three'
import { scene, socket } from '@app/apriltag'
import { camera_list, CameraObject, found_tag_list, FoundTagObject, tag_list, TagObject } from '@app/data/objects'
import { createMatrixTR, createMatrixT } from '@app/util'
import { PickHelper } from '@app/PickHelper'
import { CamRecord, FoundTagRecord, ScanResults, TagIdent, TagRecord } from '@app/data/network_objects'
import { cams_obj, tags_obj } from './models'
import { select_camera, select_found_tag, select_tag } from '@app/ui/object_selection'

let el_list: HTMLElement = null;

function CreateListElement(name: string, id: string, attribute: string, count: string = null, count_bg: string = 'text-bg-secondary') {
	var item = document.createElement('button');
	item.className = 'list-group-item d-flex justify-content-between align-items-center';
	item.textContent = name;
	item.id = id;

	item.setAttribute('ltype', attribute);

	var el_count = document.createElement('span');
	el_count.className = `badge ${ count_bg } rounded-pill ms-3`;
	el_count.innerText = count;
	item.appendChild(el_count)

	return item;
}

function ClearType(ltype: string) {
	el_list.querySelectorAll(`[ltype="${ltype}"]`).forEach((el) => {
		el.remove();
	});
}


/*
let found_tags_obj: Object3D = null
let found_tags: { [ident: string]: { el: HTMLButtonElement, objs: Object3D[] } } = {}
async function ParseFoundTags(data: {
	ident: string,
	size: number,
	cams: { [id: number]: number[] }
}[]) {
	var active_list = {}
	for (const ident in found_tags) {
		active_list[ident] = found_tags[ident].el.classList.contains('active')
		found_tags[ident].el.remove()
		found_tags[ident].objs.forEach(obj => obj.removeFromParent())
		delete found_tags[ident]
	}

	if (!found_tags_obj) {
		found_tags_obj = new Object3D()
		scene.add(found_tags_obj)
	}

	var el_tags_found = document.getElementById('tags-found').nextSibling
	for (const i in data) {
		var ident = data[i].ident
		var size = data[i].size
		var cams = data[i].cams
		var active = active_list[ident] ?? false

		var model = await LoadTagModel(ident, size)
		model.visible = active

		var models = []
		for (const cam_id in cams) {
			var trans = cams[cam_id].length > 0 ? createMatrixT(cams[cam_id]) : null
			if (trans == null) continue

			var m = model.clone()
			m.name = `${ident}-${cam_id}`
			trans.decompose(m.position, m.quaternion, m.scale)
			found_tags_obj.add(m)
		}

		var el = document.createElement('button')
		el.className = 'list-group-item list-group-item-action d-flex justify-content-between align-items-center'
		if (active) el.classList.add('active')
		el.innerText = ident
		el.id = ident

		var num = document.createElement('span')
		num.className = 'badge rounded-pill'
		num.classList.add(models.length == 0 ? 'text-bg-warning' : 'text-bg-secondary')
		num.innerText = Object.keys(cams).length.toString()
		el.appendChild(num)

		el_tags_found.parentElement.insertBefore(el, el_tags_found)

		el.onclick = (event) => {
			var tag = found_tags[(event.target as HTMLButtonElement).id]
			var vis = tag.el.classList.toggle('active')
			tag.objs.forEach(obj => obj.visible = vis)
		}

		found_tags[ident] = {
			el: el,
			objs: models
		}
	}

	on_refresh()
}
socket.on('found_tags', ParseFoundTags)


async function ParseKnownTags(data: {
	tag: {
		id: string,
		name: string,
		size: number,
		static: boolean,
		transform: number[]
	},
	cams: string[]
}[]) {
	var el_tags_known = document.getElementById('tags-known').nextSibling
	//for (const ident in known_tag_list) {
	//	known_tag_list[ident].el.remove()
	//	PickHelper.removeListeners(known_tag_list[ident].obj)
	//	known_tag_list[ident].obj.removeFromParent()
	//	delete known_tag_list[ident]
	//}

	for (const i in data) {
		var tag = data[i].tag
		var trans = tag.transform.length > 0 ? createMatrixT(tag.transform) : null

		if (!(tag.ident in known_tag_list)) {
			var model = await LoadTagModel(tag.ident, tag.size)
			model.name = tag.ident
			scene.add(model)

			var el = document.createElement('button')
			el.className = 'list-group-item list-group-item-action d-flex justify-content-between align-items-center'
			el.id = tag.ident

			el_tags_known.parentElement.insertBefore(el, el_tags_known)

			PickHelper.addListener(model, (event, m) => {
				on_tag_select(event, m.name)
			})
			el.onclick = (event) => {
				on_tag_select(event, (event.target as HTMLButtonElement).id)
			}

			known_tag_list[tag.id] = {
				obj: model,
				el: el,
				static: tag.static,
				cams: data[i].cams,
				id: tag.id,
				name: tag.name
			}
		}


		known_tag_list[tag.ident].el.innerText = tag.name

		var num = document.createElement('span')
		num.className = 'badge rounded-pill'
		num.classList.add(trans == null ? 'text-bg-warning' : tag.static ? 'text-bg-primary' : 'text-bg-secondary')
		num.innerText = data[i].cams.length.toString()
		known_tag_list[tag.ident].el.appendChild(num)

		known_tag_list[tag.ident].obj.visible = trans != null
		if (trans != null)
			trans.decompose(
				known_tag_list[tag.ident].obj.position,
				known_tag_list[tag.ident].obj.quaternion,
				known_tag_list[tag.ident].obj.scale
			)
	}

	on_refresh()
}
socket.on('tags', ParseKnownTags)

async function ParseCameras(data) {
	var el_cams = document.getElementById('cameras').nextSibling
	//for (const ident in camera_list) {
	//	camera_list[ident].el.remove()
	//	PickHelper.removeListeners(camera_list[ident].obj)
	//	camera_list[ident].obj.removeFromParent()
	//	delete camera_list[ident]
	//}

	var m = await LoadCamModel()

	for (const i in data) {
		var cam = data[i]
		var trans = cam.transform.length > 0 ? createMatrixT(cam.transform) : null

		if (!(cam.id in camera_list)) {
			var model = m.clone()
			model.name = cam.id
			model.visible = trans != null
			if (trans != null) trans.decompose(model.position, model.quaternion, model.scale)
			scene.add(model)

			var el = document.createElement('button')
			el.className = 'list-group-item list-group-item-action d-flex justify-content-between align-items-center'
			el.id = `cam${cam.id}`

			el_cams.parentElement.insertBefore(el, el_cams)

			PickHelper.addListener(model, (event, m) => {
				on_cam_select(event, parseInt(m.name))
			})
			el.onclick = (event) => {
				on_cam_select(event, parseInt((event.target as HTMLButtonElement).id.substring(3)))
			}

			camera_list[cam.id] = {
				obj: model,
				el: el,
				id: cam.id,
				name: cam.name
			};
		}

		camera_list[cam.id].el.innerText = cam.name

		var num = document.createElement('span')
		num.className = 'badge rounded-pill'
		num.classList.add(trans == null ? 'text-bg-warning' : 'text-bg-secondary')
		num.innerText = '-1'
		camera_list[cam.id].el.appendChild(num)

		camera_list[cam.id].obj.visible = trans != null
		if (trans != null)
			trans.decompose(
				camera_list[cam.id].obj.position,
				camera_list[cam.id].obj.quaternion,
				camera_list[cam.id].obj.scale
			)
	}

	on_refresh()
}
socket.on('cams', ParseCameras)
*/

async function FetchDetectors() {
	var el_detectors = document.getElementById('detectors')
	var data = (await (await fetch('detectors')).json()) as { name: string, id: string }[];

	ClearType('detector');


	var el_next = el_detectors;
	for (const detector of data) {
		let el = CreateListElement(detector.name, detector.id, 'detector')
		el.addEventListener('click', (e) => {
			e.preventDefault();
			window.Modal.open(`detectors/${detector.id}`)
				.then(FetchDetectors)
				.catch(() => { });
		})
		el.addEventListener('contextmenu', (e) => {
			e.preventDefault();
			window.Modal.open(`detectors/${detector.id}`)
				.then(FetchDetectors)
				.catch(() => { });
		})

		el_next.after(el);
		el_next = el;
	}

	var el_n_detectors = el_detectors.lastElementChild as HTMLSpanElement;
	el_n_detectors.innerText = data.length ? data.length.toString() : '+'
}

async function FetchCameras() {
	var el_cameras = document.getElementById('cameras')
	var data = (await (await fetch('/cameras/list')).json()) as CamRecord[];

	ClearType('camera');

	var to_remove = Array.from(camera_list.keys());

	var el_next = el_cameras;
	for (const camera of data) {
		let el = CreateListElement(camera.name, camera.id, 'camera')

		let cam: CameraObject;
		if (camera_list.has(camera.id)) {
			cam = camera_list.get(camera.id);
		}
		else {
			cam = new CameraObject()
			camera_list.set(camera.id, cam);
		}
		cam.set(el, camera);

		el.addEventListener('click', (e) => {
			e.preventDefault();
			select_camera(e, cam, 'list');
		});
		el.addEventListener('contextmenu', (e) => {
			e.preventDefault();
			window.Modal.open(`/cameras/${camera.id}`)
				.then(FetchCameras)
				.catch(() => { });
		})
		el_next.after(el);
		el_next = el;

		var i = to_remove.indexOf(camera.id)
		if (i > -1) to_remove.splice(i, 1);
	}

	for (const id of to_remove) camera_list.get(id).remove();

	var el_n_cameras = el_cameras.lastElementChild as HTMLSpanElement;
	el_n_cameras.innerText = data.length ? data.length.toString() : '+'
}

async function FetchTags() {
	var el_known = document.getElementById('tags-known')
	var data = await (await fetch('tags')).json() as Record<TagIdent, TagRecord>;

	ClearType('tag');

	var to_remove = Array.from(tag_list.keys());

	var el_next: HTMLElement = el_known;
	for (const [id, d_tag] of Object.entries(data)) {
		let num_cams = Object.keys(d_tag.detections).length;
		let el = CreateListElement(d_tag.name, id, 'tag', num_cams ? num_cams.toString() : null);

		let tag: TagObject;
		if (tag_list.has(id)) {
			tag = tag_list.get(id);
		}
		else {
			tag = new TagObject()
			tag_list.set(id, tag);
		}
		tag.set(el, id, d_tag);

		el.addEventListener('click', (e) => {
			e.preventDefault();
			select_tag(e, tag, 'list');
		});
		el.addEventListener('contextmenu', (e) => {
			e.preventDefault();
			window.Modal.open(`tags/${id}`)
				.then(FetchTags).catch(() => { });;
		});

		el_next.after(el);
		el_next = el;

		var i = to_remove.indexOf(id)
		if (i > -1) to_remove.splice(i, 1);
	}

	for (const id of to_remove) tag_list.get(id).remove();

	var el_n_known = el_known.lastElementChild as HTMLSpanElement;
	var n_known = Object.keys(data).length;
	el_n_known.innerText = n_known ? n_known.toString() : '+';

	RefreshCamCounts();
}

async function FetchFoundTags() {
	var el_found = document.getElementById('tags-found')
	var data = await (await fetch('tags/found')).json() as Record<TagIdent, FoundTagRecord>;

	ClearType('found');

	var to_remove = Array.from(found_tag_list.entries().filter(([s, i]) => !i.pinned).map(([s, i]) => s));

	var el_next = el_found;
	for (const [ident, cams] of Object.entries(data)) {
		let num_cams = Object.keys(cams).length;
		let el = CreateListElement(ident, ident, 'found', num_cams.toString());

		let tag: FoundTagObject;
		if (found_tag_list.has(ident)) {
			tag = found_tag_list.get(ident);
		}
		else {
			tag = new FoundTagObject()
			found_tag_list.set(ident, tag);
		}
		tag.set(el, ident, cams);

		el.addEventListener('click', (e) => {
			e.preventDefault();
			select_found_tag(e, tag, 'list');
		});
		el.addEventListener('contextmenu', (e) => {
			e.preventDefault();
			window.Modal.open(`tags/found/${ident}`)
				.then(() => { FetchTags(); FetchFoundTags() }).catch(() => { });
		});

		el_next.after(el);
		el_next = el;

		var i = to_remove.indexOf(ident)
		if (i > -1) to_remove.splice(i, 1);
	}

	for (const id of to_remove) found_tag_list.get(id).remove();

	var el_n_found = el_found.lastElementChild as HTMLSpanElement;
	var n_found = Object.keys(data).length;
	el_n_found.innerText = n_found ? n_found.toString() : '+';

	RefreshCamCounts();
}

function RefreshCamCounts() {
	for (const cam of camera_list.values()) cam.fetch_tags();
}

export function Scan() {
	fetch('tags/scan?noreturn').then(() => {
		FetchTags();
		FetchFoundTags();
	}).catch(() => { });
}

export function Refresh() {
	FetchDetectors()
	FetchCameras()
	FetchTags()
	FetchFoundTags()
	Scan()
}

window.addEventListener('DOMContentLoaded', () => {

	el_list = document.getElementById('object-list');

	var btn_refresh = document.getElementById('tags-refresh') as HTMLButtonElement;
	btn_refresh.addEventListener('click', (e) => {
		Refresh();
	});


	var btn_detector = document.getElementById('new-detector') as HTMLLinkElement;
	btn_detector.addEventListener('click', (e) => {
		e.preventDefault();
		window.Modal.open(btn_detector.href)
			.then(FetchDetectors)
			.catch(() => { });
	});

	var btn_camera = document.getElementById('new-camera') as HTMLLinkElement;
	btn_camera.addEventListener('click', (e) => {
		e.preventDefault();
		window.Modal.open(btn_camera.href)
			.then(FetchCameras)
			.catch(() => { });
	});

	Refresh();
});