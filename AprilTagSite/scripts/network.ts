import * as THREE from 'three'
import { createMatrixTR, createMatrixT } from './util'
import { PickHelper } from './PickHelper'

let texLoader = new THREE.TextureLoader()


export async function LoadTagModel(ident: string, size = 1): Promise<THREE.Object3D> {
	var geom = new THREE.PlaneGeometry(size, size)

	var tex = await texLoader.loadAsync(`tags/image/${ident}.png`)
	tex.magFilter = THREE.NearestFilter

	var mat = new THREE.MeshBasicMaterial({ map: tex })
	mat.side = THREE.DoubleSide

	return new THREE.Mesh(geom, mat)
}

export type TagInfo = {
	known: boolean,
	obj: THREE.Object3D,
	el: HTMLButtonElement,
	transform: THREE.Matrix4,
	static: boolean,
	cams: { [cam_id: number]: THREE.Matrix4 }
}

export let tag_list: { [ident: string]: TagInfo } = {}
export let selected_tag: TagInfo = null

export async function RefreshFoundTags(scene: THREE.Scene) {

	var data = await (await fetch('tags/found/list')).json()

	for (const ident in data) {
		var size = data[ident].size
		var cams = data[ident].cams

		var model = await LoadTagModel(ident, size)
		model.add(new THREE.AxesHelper(size))

		for (const i in cams) {
			var m = model.clone(true)

			m.name = `${ident}-${cams[i].cam.id}`

			var pose_t = cams[i].data.pose_t
			var pose_r = cams[i].data.pose_r
			var mat = createMatrixTR(pose_t, pose_r)

			m.applyMatrix4(mat)

			scene.add(m)
		}
	}
}


export async function RefreshKnownTags(scene: THREE.Scene) {
	var data = await (await fetch('tags/list')).json()

	var el_tags_known = document.getElementById('tags-known').nextSibling
	for (const ident in tag_list) {
		if (tag_list[ident].known) {
			tag_list[ident].el.remove()
			PickHelper.removeListeners(tag_list[ident].obj)
			tag_list[ident].obj.removeFromParent()
			delete tag_list[ident]
		}
	}


	for (const ent in data) {
		var tag = data[ent].tag
		var cams = data[ent].cams
		var cam_data = {}

		for (const i in cams) {
			var cam = cams[i]
			cam_data[cam.id] = createMatrixTR(cam.data.pose_t, cam.data.pose_r)
		}

		var trans = tag.transform.length > 0 ? createMatrixT(tag.transform) : null

		var model = await LoadTagModel(tag.ident, tag.size)
		model.name = tag.ident
		model.visible = trans != null
		if (trans != null) model.applyMatrix4(trans)
		scene.add(model)

		var el = document.createElement('button')
		el.className = 'list-group-item list-group-item-action d-flex justify-content-between align-items-center'
		el.innerText = tag.name
		el.id = tag.ident

		var num = document.createElement('span')
		num.className = 'badge rounded-pill'
		num.classList.add(trans == null ? 'text-bg-warning' : tag.static ? 'text-bg-primary' : 'text-bg-secondary')
		num.innerText = cams.length
		el.appendChild(num)

		el_tags_known.parentElement.insertBefore(el, el_tags_known)

		PickHelper.addListener(model, (m) => {
			on_tag_select(m.name)
		})
		el.onclick = (event) => {
			on_tag_select((event.target as HTMLButtonElement).id)
		}

		tag_list[tag.ident] = {
			known: true,
			obj: model,
			el: el,
			transform: trans,
			static: tag.static,
			cams: cam_data
		}
	}
}

function on_tag_select(ident: string = '') {
	if (selected_tag) {
		selected_tag.el.classList.toggle('active', false)
		selected_tag = null
	}

	if (ident in tag_list) {
		selected_tag = tag_list[ident]
		selected_tag.el.classList.toggle('active', true)
	}
}
PickHelper.add_default_listener(on_tag_select)
