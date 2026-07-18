import { CameraObject, FoundTagObject, TagObject } from "@app/data/objects";
import { PickHelper } from "@app/PickHelper";


type SelectSource = 'list' | '3D';
type Selectable = CameraObject | TagObject | FoundTagObject;

export class ObjectSelector {
	
	private static selected: Selectable = null

	static get_selected() { return this.selected; }
	static is_selected(obj: Selectable) { return this.selected == obj; }

	static async select_camera(ev: PointerEvent | MouseEvent, cam: CameraObject, source: SelectSource) {
		if (this.is_selected(cam)) return;
		this.deselect(ev, 'select');

		console.log(ev, cam, source)

		this.selected = cam;
		cam.list_el.classList.toggle("active", true);
		let obj = await cam.get_obj();
	}

	static async select_tag(ev: PointerEvent | MouseEvent, tag: TagObject, source: SelectSource) {
		if (this.is_selected(tag)) return;
		this.deselect(ev, 'select');

		console.log(ev, tag, source)
		
		this.selected = tag;
		tag.list_el.classList.toggle("active", true);
	}

	static async select_found_tag(ev: PointerEvent | MouseEvent, tag: FoundTagObject, source: SelectSource) {
		if (this.is_selected(tag)) return;
		this.deselect(ev, 'select');

		console.log(ev, tag, source)
		
		this.selected = tag;
		tag.list_el.classList.toggle("active", true);
	}

	static async deselect(ev: PointerEvent | MouseEvent, source: SelectSource | 'delete' | 'select') {
		if (this.selected) {
			this.selected.list_el.classList.toggle("active", false);
		}
		if (source == 'select') return;
		console.log(ev, this.selected, source)
		this.selected = null;
	}
}



PickHelper.default_listeners.push((e) => ObjectSelector.deselect(e, '3D'));