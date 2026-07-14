import * as THREE from 'three'
import { ATagObject } from '@app/data/objects'
import { scene } from '@app/apriltag';

THREE.Cache.enabled = true;
let texLoader = new THREE.TextureLoader()

export let tags_obj = new THREE.Object3D();
export let found_tags_obj = new THREE.Object3D();
export let cams_obj = new THREE.Object3D();

window.addEventListener('load', () => {
	scene.add(tags_obj, found_tags_obj, cams_obj);
})

export async function LoadTagModel(tag: ATagObject): Promise<THREE.Object3D> {
	var geom = new THREE.PlaneGeometry(1)

	var tex = texLoader.load(`tags/image/${tag.ident}.png`)
	tex.magFilter = THREE.NearestFilter
	tex.flipY = false

	var mat = new THREE.MeshBasicMaterial({ map: tex })
	mat.side = THREE.DoubleSide

	var model = new THREE.Mesh(geom, mat)
	model.add(new THREE.AxesHelper(1))
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