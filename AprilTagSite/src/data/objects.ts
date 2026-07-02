import { Object3D } from 'three'

export type Detector = {
	ident: string,
	name: string
}

export type TagInfo = {
	obj: Object3D,
	el: HTMLButtonElement,
	static: boolean,
	cams: string[],
	id: string
	name: string
}

export type CameraInfo = {
	obj: Object3D,
	el: HTMLButtonElement,
	id: string
	name: string
}

export let known_tag_list: { [ident: string]: TagInfo } = {}
export let camera_list: { [ident: string]: CameraInfo } = {}
