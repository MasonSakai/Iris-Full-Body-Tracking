import { Matrix4 } from 'three'
import { scene, socket } from '@app/apriltag'
import { camera_list, CameraObject, found_tag_list, FoundTagObject, tag_list, TagObject } from '@app/data/objects'
import { PickHelper } from '@app/PickHelper'
import { CamRecord, FoundTagRecord, ScanResults, TagIdent, TagRecord } from '@app/data/network_objects'
import { ObjectSelector } from '@app/ui/object_selector'

let el_list: HTMLElement = null;

function CreateListElement(name: string, id: string, attribute: string, count: string = null, count_bg: string = 'text-bg-secondary') {
	var item = document.createElement('button');
	item.className = 'btn btn-outline-secondary list-group-item d-flex justify-content-between align-items-center';
	item.textContent = name;
	item.id = id;

	item.setAttribute('ltype', attribute);
	item.toggleAttribute('keepfocus', true);

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
			el.classList.toggle('active', ObjectSelector.is_selected(cam));
		}
		else {
			cam = new CameraObject()
			camera_list.set(camera.id, cam);
		}
		cam.set(el, camera).then(async () => {
			PickHelper.addListener(await cam.get_obj(), (e) => ObjectSelector.select_camera(e, cam, '3D'));
		});

		el.addEventListener('click', (e) => {
			e.preventDefault();
			ObjectSelector.select_camera(e, cam, 'list');
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
			el.classList.toggle('active', ObjectSelector.is_selected(tag));
		}
		else {
			tag = new TagObject()
			tag_list.set(id, tag);
		}
		tag.set(el, id, d_tag).then(async () => {
			PickHelper.addListener(await tag.get_obj(), (e) => ObjectSelector.select_tag(e, tag, '3D'));
		});

		el.addEventListener('click', (e) => {
			e.preventDefault();
			ObjectSelector.select_tag(e, tag, 'list');
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

	var to_remove = Array.from(found_tag_list.keys());

	var el_next = el_found;
	for (const [ident, cams] of Object.entries(data)) {
		let num_cams = Object.keys(cams).length;
		let el = CreateListElement(ident, ident, 'found', num_cams.toString());

		let tag: FoundTagObject;
		if (found_tag_list.has(ident)) {
			tag = found_tag_list.get(ident);
			el.classList.toggle('active', ObjectSelector.is_selected(tag));
		}
		else {
			tag = new FoundTagObject()
			found_tag_list.set(ident, tag);
		}
		tag.set(el, ident, cams).then(async () => {
			PickHelper.addListener(await tag.get_obj(), (e) => ObjectSelector.select_found_tag(e, tag, '3D'));
		});

		el.addEventListener('click', (e) => {
			e.preventDefault();
			ObjectSelector.select_found_tag(e, tag, 'list');
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