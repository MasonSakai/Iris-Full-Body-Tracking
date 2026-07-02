import * as THREE from 'three'

let texLoader = new THREE.TextureLoader()

export async function LoadTagModel(ident: string, size = 1): Promise<THREE.Object3D> {
	var geom = new THREE.PlaneGeometry(size, size)

	var tex = await texLoader.loadAsync(`tags/image/${ident}.png`)
	tex.magFilter = THREE.NearestFilter
	tex.flipY = false

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