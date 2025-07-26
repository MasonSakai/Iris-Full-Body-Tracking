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

		canvas.addEventListener('mousemove', PickHelper.setPickPosition);
		canvas.addEventListener('mouseout', PickHelper.clearPickPosition);
		canvas.addEventListener('mouseleave', PickHelper.clearPickPosition);


		canvas.addEventListener('mousedown', PickHelper.on_mouse_down)
		canvas.addEventListener('mouseup', PickHelper.on_mouse_up)

	}
	static pick(scene, camera, time) {

		// cast a ray through the frustum
		PickHelper.raycaster.setFromCamera(PickHelper.pickPosition, camera);
		// get the list of objects the ray intersected
		const intersectedObjects = PickHelper.raycaster.intersectObjects(scene.children, false);
		for (const i in intersectedObjects) {
			var obj = intersectedObjects[i].object
			if (obj.visible) {
				PickHelper.pickedObject = obj
				return
			}
		}
		PickHelper.pickedObject = null

	}

	static md_pos: { x: number, y: number}
	static on_mouse_down(event: MouseEvent) {
		PickHelper.md_pos = { x: event.x, y: event.y }
	}

	static on_mouse_up(event: MouseEvent) {
		if (Math.abs(event.x - PickHelper.md_pos.x) > 5
			|| Math.abs(event.y - PickHelper.md_pos.y) > 5) return

		if (!(PickHelper.pickedObject && PickHelper.pickedObject.id in PickHelper.listeners)) {
			PickHelper.default_listeners.forEach(f => f())
			return
		}

		PickHelper.listeners[PickHelper.pickedObject.id]
			.forEach(f => f(PickHelper.pickedObject))
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

	static listeners: { [id: number]: ((obj: THREE.Object3D) => void)[] } = {}
	static default_listeners: (() => void)[] = []

	static removeListeners(obj: THREE.Object3D) {
		delete PickHelper.listeners[obj.id]
	}
	static addListener(obj: THREE.Object3D, func: (obj: THREE.Object3D) => void) {
		if (obj.id in PickHelper.listeners)
			PickHelper.listeners[obj.id].push(func)
		else PickHelper.listeners[obj.id] = [func]
	}

	static add_default_listener(func: () => void) {
		PickHelper.default_listeners.push(func)
	}
}