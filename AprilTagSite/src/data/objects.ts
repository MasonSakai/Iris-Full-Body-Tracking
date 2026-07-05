import { Object3D } from 'three'
import { TagIdent, CameraIdent, FoundTagIdent } from '@app/data/network_objects'

export type Detector = {
	ident: string,
	name: string
}

export type TagInfo = {
	obj: Object3D,
	el: HTMLButtonElement,
	static: boolean,
	cams: string[],
	id: TagIdent
	name: string
}

export type CameraInfo = {
	obj: Object3D,
	el: HTMLButtonElement,
	id: CameraIdent
	name: string
}

export let known_tag_list: { [ident: TagIdent]: TagInfo } = {}
export let camera_list: { [ident: CameraIdent]: CameraInfo } = {}
//export let found_tag_list: { [ident: FoundTagIdent]: TagInfo }