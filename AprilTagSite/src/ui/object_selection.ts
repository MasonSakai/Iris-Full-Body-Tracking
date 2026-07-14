import { CameraObject, FoundTagObject, TagObject } from "@app/data/objects";


export function select_camera(ev: PointerEvent, cam: CameraObject, source: 'list' | '3D') {
	console.log(ev, cam, source)
}

export function select_tag(ev: PointerEvent, tag: TagObject, source: 'list' | '3D') {
	console.log(ev, tag, source)
}

export function select_found_tag(ev: PointerEvent, tag: FoundTagObject, source: 'list' | '3D') {
	console.log(ev, tag, source)
}