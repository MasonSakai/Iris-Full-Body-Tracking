import { Object3D, Matrix4, Vector3 } from 'three'
import { TagIdent, CameraId, TagID, CamRecord, TagRecord, FoundTagRecord } from '@app/data/network_objects'
import { cams_obj, LoadCamModel, LoadTagModel } from '@app/ui/models'
import { CreateMatrix, CorrectMatrix } from '@app/util'
import { PickHelper } from '@app/PickHelper'
import { ObjectSelector } from '@app/ui/object_selector'

export class DisplayObject {
	obj: Object3D
	list_el: HTMLButtonElement
	num_el: HTMLSpanElement

	protected showing_preview: boolean = false;
	transform: Matrix4;

	set_transform(mat: Matrix4, preview: boolean = false, size: number = 1) {
		if (!preview) this.transform = mat;
		if (this.showing_preview && !preview) return;
		this.showing_preview = preview;
		this.obj.visible = mat != null;
		if (mat != null) {
			CorrectMatrix(mat).decompose(this.obj.position, this.obj.quaternion, new Vector3());
			this.obj.scale.setScalar(size);
			this.obj.updateMatrix();
		}
	}

	clear_preview() {
		this.showing_preview = false;
		this.set_transform(this.transform);
	}

	get_name() { throw new Error("Method not implemented."); }

}

export class CameraObject extends DisplayObject {
	name: string
	id: CameraId

	active: string | false

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
		this.set_transform(CreateMatrix(cam.transform));
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
		if (this.obj) {
			this.obj.removeFromParent();
			PickHelper.removeListener(this.obj);
		}
		if (ObjectSelector.is_selected(this)) ObjectSelector.deselect(null, 'delete');
		camera_list.delete(this.id)
	}

	get_name() { return this.name; }
}

export class TagDetection {
	num: number
	trans: Matrix4
	v_pos: number
	v_mar: number
}
export class FoundTagDetection extends TagDetection {
	size: number
};

export class ATagObject extends DisplayObject {
	ident: TagIdent

	detections: Map<CameraId, any>

	size: number = 0.1;

	async get_obj() {
		if (this.obj == null) {
			this.obj = await LoadTagModel(this);
			cams_obj.add(this.obj);
		}
		return this.obj;
	}

	set_transform(mat: Matrix4, preview: boolean = false, size: number = this.size) {
		return super.set_transform(mat, preview, size);
	}

	update_count() {
		this.num_el.innerText = this.detections.size.toString();
	}
}

export class TagObject extends ATagObject {
	name: string
	id: TagID

	static: boolean

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
			det.trans = CreateMatrix(d.trans);
			det.v_pos = d.v_pos;
			det.v_mar = d.v_mar;
			this.detections.set(id, det);
		}

		await this.get_obj();
		this.set_transform(CreateMatrix(d_tag.transform));
		this.set_static(d_tag.static);
	}

	set_static(is_static: boolean) {
		this.static = is_static;

		this.num_el.classList.toggle('text-bg-warning', is_static);
		this.num_el.classList.toggle('text-bg-secondary', !is_static);

		this.update_count();
	}

	remove() {
		if (this.obj) {
			this.obj.removeFromParent();
			PickHelper.removeListener(this.obj);
		}
		if (ObjectSelector.is_selected(this)) ObjectSelector.deselect(null, 'delete');
		tag_list.delete(this.id)
	}

	get_name() { return this.name; }
}

export class FoundTagObject extends ATagObject {
	detections: Map<CameraId, FoundTagDetection> = new Map()


	async set(el: HTMLButtonElement, ident: string, d_tag: FoundTagRecord) {
		this.list_el = el;
		this.num_el = el.lastElementChild as HTMLSpanElement;

		this.ident = ident;
		this.detections.clear();

		let sizes: Record<number, number> = {};

		for (const [id, d] of Object.entries(d_tag)) {
			var det = new FoundTagDetection();
			det.num = d.num;
			det.trans = CreateMatrix(d.trans);
			det.v_pos = d.v_pos;
			det.v_mar = d.v_mar;
			det.size = d.size;
			this.detections.set(id, det);
			sizes[d.size] = (sizes[d.size] || 0) + 1;
		}

		this.size = Number(Object.keys(sizes).reduce((a, b) => sizes[a] > sizes[b] ? a : b) || this.size);

		await this.get_obj();
		this.set_transform(null);
		this.update_count();
	}

	remove() {
		if (this.obj) {
			this.obj.removeFromParent();
			PickHelper.removeListener(this.obj);
		}
		if (ObjectSelector.is_selected(this)) ObjectSelector.deselect(null, 'delete');
		found_tag_list.delete(this.ident)
	}

	get_name() { return this.ident; }
}

export let tag_list = new Map<TagID, TagObject>()
export let found_tag_list = new Map<TagIdent, FoundTagObject>()
export let camera_list = new Map<CameraId, CameraObject>()