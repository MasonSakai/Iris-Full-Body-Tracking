import { Object3D, Matrix4, Vector3, Quaternion } from 'three'
import { TagIdent, CameraId, TagDetails, FoundTagDetails, TagID, CamRecord, TagRecord, FoundTagRecord } from '@app/data/network_objects'
import { cams_obj, LoadCamModel, LoadTagModel } from '@app/ui/models'
import { createMatrixT } from '@app/util'

export class CameraObject {
	obj: Object3D
	list_el: HTMLButtonElement
	num_el: HTMLSpanElement

	name: string
	id: CameraId

	active: string | false

	transform: Matrix4

	tags = {
		known: new Set<TagID>(),
		found: new Set<TagIdent>()
	}

	async set(el: HTMLButtonElement, cam: CamRecord) {
		this.list_el = el;
		this.num_el = el.lastElementChild as HTMLSpanElement;
		this.name = cam.name;
		this.id = cam.id;
		this.fetch_tags();
		await this.get_obj();
		this.set_transform(createMatrixT(cam.transform));
		this.set_active(cam.active);
	}

	fetch_tags() {
		this.tags.known.clear();
		this.tags.found.clear();

		for (const [id, tag] of tag_list)
			if (tag.detections.has(this.id))
				this.tags.known.add(id)

		for (const [ident, tag] of found_tag_list)
			if (tag.detections.has(this.id))
				this.tags.found.add(ident)

		this.update_count();
	}

	async get_obj() {
		if (this.obj == null) {
			this.obj = await LoadCamModel();
			cams_obj.add(this.obj);
		}
		return this.obj;
	}

	set_transform(mat: Matrix4) {
		this.transform = mat;

		this.obj.visible = mat != null;
		if (mat != null) {
			mat.decompose(this.obj.position, this.obj.quaternion, new Vector3());
			this.obj.updateMatrix();
		}
	}

	set_active(active: string | false) {
		this.active = active;

		this.num_el.classList.toggle('text-bg-danger', !!active);
		this.num_el.classList.toggle('text-bg-secondary', !active);

		this.update_count();
	}

	update_count() {
		var num = this.tags.known.size + this.tags.found.size;
		this.num_el.innerText = num > 0 ? num.toString() : (this.active ? '\u00A0' : null);
	}

	remove() {
		if (this.obj) this.obj.removeFromParent();
		camera_list.delete(this.id)
	}
}

export class TagDetection {
	num: number
	pos: Vector3
	rot: Quaternion
	v_pos: number
	v_mar: number
}
export class FoundTagDetection extends TagDetection {
	size: number
};

export class ATagObject {
	obj: Object3D
	list_el: HTMLButtonElement
	num_el: HTMLSpanElement

	ident: TagIdent

	detections: Map<CameraId, any>

	async get_obj() {
		if (this.obj == null) {
			this.obj = await LoadTagModel(this);
			cams_obj.add(this.obj);
		}
		return this.obj;
	}

	set_transform(mat: Matrix4) {
		this.obj.visible = mat != null;
		if (mat != null) {
			mat.decompose(this.obj.position, this.obj.quaternion, new Vector3());
			this.obj.updateMatrix();
		}
	}

	update_count() {
		this.num_el.innerText = this.detections.size.toString();
	}
}

export class TagObject extends ATagObject {
	name: string
	id: TagID

	static: boolean
	size: number

	transform: Matrix4

	detections: Map<CameraId, TagDetection> = new Map()

	async set(el: HTMLButtonElement, id: string, d_tag: TagRecord) {
		this.list_el = el;
		this.num_el = el.lastElementChild as HTMLSpanElement;

		this.id = id;

		this.name = d_tag.name;
		this.ident = d_tag.ident;
		this.size = d_tag.size;
		this.detections.clear();

		for (const [id, d] of Object.entries(d_tag.detections)) {
			var det = new TagDetection();
			det.num = d.num;
			det.pos = new Vector3(d.pos[0], d.pos[1], d.pos[2])
			det.rot = new Quaternion(d.rot[0], d.rot[1], d.rot[2], d.rot[3])
			det.v_pos = d.v_pos;
			det.v_mar = d.v_mar;
			this.detections.set(id, det);
		}

		await this.get_obj();
		this.set_transform(createMatrixT(d_tag.transform));
		this.set_static(d_tag.static);
	}

	set_transform(mat: Matrix4) {
		this.transform = mat;
		super.set_transform(mat);
	}

	set_static(is_static: boolean) {
		this.static = is_static;

		this.num_el.classList.toggle('text-bg-warning', is_static);
		this.num_el.classList.toggle('text-bg-secondary', !is_static);

		this.update_count();
	}

	remove() {
		if (this.obj) this.obj.removeFromParent();
		tag_list.delete(this.id)

		for (const cam in this.detections) {
			console.log(cam)
		}
	}
}

export class FoundTagObject extends ATagObject {
	pinned: boolean = false
	detections: Map<CameraId, FoundTagDetection> = new Map()


	async set(el: HTMLButtonElement, ident: string, d_tag: FoundTagRecord) {
		this.list_el = el;
		this.num_el = el.lastElementChild as HTMLSpanElement;

		this.ident = ident;
		this.detections.clear();

		for (const [id, d] of Object.entries(d_tag)) {
			var det = new FoundTagDetection();
			det.num = d.num;
			det.pos = new Vector3(d.pos[0], d.pos[1], d.pos[2])
			det.rot = new Quaternion(d.rot[0], d.rot[1], d.rot[2], d.rot[3])
			det.v_pos = d.v_pos;
			det.v_mar = d.v_mar;
			det.size = d.size;
			this.detections.set(id, det);
		}

		await this.get_obj();
		this.set_transform(null);
		this.update_count();
	}

	set_pinned(is_pinned: boolean) {
		this.pinned = is_pinned;

		this.num_el.classList.toggle('text-bg-warning', is_pinned);
		this.num_el.classList.toggle('text-bg-secondary', !is_pinned);

		this.update_count();
	}

	remove() {
		if (this.obj) this.obj.removeFromParent();
		found_tag_list.delete(this.ident)
	}
}

export let tag_list = new Map<TagID, TagObject>()
export let found_tag_list = new Map<TagIdent, FoundTagObject>()
export let camera_list = new Map<CameraId, CameraObject>()