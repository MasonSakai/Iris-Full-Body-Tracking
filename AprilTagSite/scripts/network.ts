import * as THREE from 'three'
import { createMatrixTR, createMatrixT } from './util'
import { PickHelper } from './PickHelper'
import './ui'
import { scene, controls, camera, LookAt } from './apriltag3D'
import { io } from 'socket.io-client'

let texLoader = new THREE.TextureLoader()

export let socket = io('/apriltag')

export async function LoadTagModel(ident: string, size = 1): Promise<THREE.Object3D> {
	var geom = new THREE.PlaneGeometry(size, size)

	var tex = await texLoader.loadAsync(`tags/image/${ident}.png`)
	tex.magFilter = THREE.NearestFilter

	var mat = new THREE.MeshBasicMaterial({ map: tex })
	mat.side = THREE.DoubleSide

	var model = new THREE.Mesh(geom, mat)
	model.add(new THREE.AxesHelper(size))
	return model
}

export async function LoadCamModel(): Promise<THREE.Object3D> {
	var geom = new THREE.BoxGeometry(0.2, 0.2, 0.1)

	var mat = new THREE.MeshBasicMaterial({ color: 0xFF0000 })

	var model = new THREE.Mesh(geom, mat)
	model.add(new THREE.AxesHelper(0.3))
	return model
}

async function LoadPoseModel(): Promise<THREE.Object3D> {
	var geom = new THREE.SphereGeometry(0.05)

	var mat = new THREE.MeshBasicMaterial({ color: 0x00FF00 })

	var model = new THREE.Mesh(geom, mat)
	model.add(new THREE.AxesHelper(0.1))
	return model
}

export type TagInfo = {
	obj: THREE.Object3D,
	el: HTMLButtonElement,
	static: boolean,
	cams: number[],
	ident: string
}

export type CameraInfo = {
	obj: THREE.Object3D,
	el: HTMLButtonElement,
	ident: number
}


function on_tag_select(event: MouseEvent, ident: string = '') {
	if (selected) {
		selected.el.classList.toggle('active', false)
		selected = null
	}

	if (ident in known_tag_list) {
		selected = known_tag_list[ident]
		selected.el.classList.toggle('active', true)

		LookAt(selected.obj)
	}
	selectionChange_listeners.forEach(f => f(event))
}

function on_cam_select(event: MouseEvent, id: number = -1) {
	if (selected) {
		selected.el.classList.toggle('active', false)
		selected = null
	}

	if (id in camera_list) {
		selected = camera_list[id]
		selected.el.classList.toggle('active', true)

		LookAt(selected.obj)
	}
	selectionChange_listeners.forEach(f => f(event))
}
PickHelper.add_default_listener(on_tag_select)

export let known_tag_list: { [ident: string]: TagInfo } = {}
export let camera_list: { [id: number]: CameraInfo } = {}

export let selected: TagInfo | CameraInfo = null
export let selectionChange_listeners: ((event: MouseEvent) => void)[] = []

export let refresh_listeners: (() => void)[] = []

let found_tags_obj: THREE.Object3D = null
let found_tags: { [ident: string]: { el: HTMLButtonElement, objs: THREE.Object3D[] } } = {}
async function ParseFoundTags(data: {
	ident: string,
	size: number,
	cams: { [id: number]: number[]}
}[]) {
	var active_list = {}
	for (const ident in found_tags) {
		active_list[ident] = found_tags[ident].el.classList.contains('active')
		found_tags[ident].el.remove()
		found_tags[ident].objs.forEach(obj => obj.removeFromParent())
		delete found_tags[ident]
	}

	if (!found_tags_obj) {
		found_tags_obj = new THREE.Object3D()
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
		id: number,
		ident: string,
		name: string,
		size: number,
		static: boolean,
		transform: number[]
	},
	cams: number[]
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

			known_tag_list[tag.ident] = {
				obj: model,
				el: el,
				static: tag.static,
				cams: data[i].cams,
				ident: tag.ident
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
				ident: cam.id
			}
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

var refreshTimeout = null
function ResetRefreshTimeout() {
	if (refreshTimeout != null)
		clearTimeout(refreshTimeout)

	refreshTimeout = setTimeout(Refresh, 5000)
}
function on_refresh() {
	ResetRefreshTimeout()
	refresh_listeners.forEach(f => f())
}
export function Refresh() {
	ResetRefreshTimeout()
	socket.emit('tags')
	socket.emit('found_tags')
	socket.emit('cams')
}

let pose_obj: THREE.Object3D = null
async function ParsePose(data) {
	if (!pose_obj) {
		pose_obj = new THREE.Object3D()
		scene.add(pose_obj)
	}

	var m = await LoadPoseModel()

	for (const ident in data) {

		var model = pose_obj.getObjectByName(ident)
		if (!model) {
			model = m.clone()
			model.name = ident
			model.matrixAutoUpdate = false
			pose_obj.add(model)
		}
		model.visible = true
		model.matrixAutoUpdate = false
		model.matrix = createMatrixT(data[ident])
	}

	for (const model of pose_obj.children) {
		if (model.name in data) continue
		model.visible = false
	}
}
socket.on('pose', ParsePose)
