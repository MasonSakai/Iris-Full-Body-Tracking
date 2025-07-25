import * as THREE from 'three'

export class PickHelper {
	static raycaster: THREE.Raycaster;
	static pickedObject: THREE.Object3D;
	static canvas: HTMLCanvasElement;

	static pickPosition: THREE.Vector2

	static init(canvas: HTMLCanvasElement) {

		PickHelper.canvas = canvas
		PickHelper.raycaster = new THREE.Raycaster();
		PickHelper.pickedObject = null;
		PickHelper.pickPosition = new THREE.Vector2()

		PickHelper.clearPickPosition()

		window.addEventListener('mousemove', PickHelper.setPickPosition);
		window.addEventListener('mouseout', PickHelper.clearPickPosition);
		window.addEventListener('mouseleave', PickHelper.clearPickPosition);


		window.addEventListener('mousedown', PickHelper.on_mouse_down)
		window.addEventListener('mouseup', PickHelper.on_mouse_up)

	}
	static pick(scene, camera, time) {

		// cast a ray through the frustum
		PickHelper.raycaster.setFromCamera(PickHelper.pickPosition, camera);
		// get the list of objects the ray intersected
		const intersectedObjects = PickHelper.raycaster.intersectObjects(scene.children, false);
		if (intersectedObjects.length) {

			// pick the first object. It's the closest one
			PickHelper.pickedObject = intersectedObjects[0].object;

		}
		else PickHelper.pickedObject = null

	}

	static md_pos: { x: number, y: number}
	static on_mouse_down(event: MouseEvent) {
		PickHelper.md_pos = { x: event.x, y: event.y }
	}

	static on_mouse_up(event: MouseEvent) {
		if (Math.abs(event.x - PickHelper.md_pos.x) > 5
			|| Math.abs(event.y - PickHelper.md_pos.y) > 5) return

		if (!PickHelper.pickedObject) return

		console.log(PickHelper.pickedObject)
	}
	
	static getCanvasRelativePosition(event) {

		const rect = PickHelper.canvas.getBoundingClientRect();
		return {
			x: (event.clientX - rect.left) * PickHelper.canvas.width / rect.width,
			y: (event.clientY - rect.top) * PickHelper.canvas.height / rect.height,
		};

	}
	static setPickPosition(event) {

		const pos = PickHelper.getCanvasRelativePosition(event);
		PickHelper.pickPosition.x = (pos.x / PickHelper.canvas.width) * 2 - 1;
		PickHelper.pickPosition.y = (pos.y / PickHelper.canvas.height) * - 2 + 1; // note we flip Y

	}

	static clearPickPosition() {

		// unlike the mouse which always has a position
		// if the user stops touching the screen we want
		// to stop picking. For now we just pick a value
		// unlikely to pick something
		PickHelper.pickPosition.x = - 100000;
		PickHelper.pickPosition.y = - 100000;

	}
}