import * as THREE from 'three'
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import '@app/ui/object_list';
import '@app/ui/placement_rules';
import "@app/ui/solver";
import { CreateMatrix } from '@app/util'
import { PickHelper } from '@app/PickHelper'

import { io } from 'socket.io-client'
export let socket = io('/apriltag')

export let canvas: HTMLCanvasElement = null;
let canvas_wrapper: HTMLDivElement = null;

export let scene = new THREE.Scene()
var ax = new THREE.AxesHelper(1)
ax.matrixAutoUpdate = false
ax.matrix.copy(CreateMatrix([
	1, 0, 0, 0,
	0, 1, 0, 0,
	0, 0, 1, 0,
	0, 0, 0, 1
]))
scene.add(ax)
export let camera = new THREE.PerspectiveCamera(75, null, 0.01, 100)
export let controls: OrbitControls = null

let renderer: THREE.WebGLRenderer = null

function render(time: number) {
	time *= 0.001  // convert time to seconds

	PickHelper.pick(scene, camera, time)

	controls.update()

	renderer.render(scene, camera)

	requestAnimationFrame(render)
}

export function canvas_resized() {
	const rect = canvas_wrapper.getBoundingClientRect();

	// Update camera parameters to prevent stretching
	camera.aspect = rect.width / rect.height;
	camera.updateProjectionMatrix();

	renderer.setSize(rect.width, rect.height, false);
}

window.addEventListener('load', () => {
	canvas_wrapper = document.getElementById('tag-canvas-wrapper') as HTMLDivElement;
	canvas = document.getElementById('tag-canvas') as HTMLCanvasElement;

	//camera.fov = 2 * Math.atan(rect.height / (2 * 240.17084283097014)) * (180 / Math.PI)
	controls = new OrbitControls(camera, canvas)
	PickHelper.init(canvas)
	renderer = new THREE.WebGLRenderer(
		{
			antialias: true,
			canvas,
			alpha: true,
			premultipliedAlpha: false,
		})

	window.onresize = canvas_resized;
	canvas_resized();

	camera.position.z = -3
	controls.update()

	requestAnimationFrame(render)
});

export function LookAt(obj: THREE.Object3D) {

	controls.target.copy(obj.position)
	controls.update()
}