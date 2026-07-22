import { CameraObject, FoundTagObject, TagObject } from "@app/data/objects";
import { PickHelper } from "@app/PickHelper";
import { PlacementRuleManager } from "./placement_rules";


type SelectSource = 'list' | '3D';
export type Selectable = CameraObject | TagObject | FoundTagObject;

export function get_name(obj: Selectable) { return obj instanceof FoundTagObject ? obj.ident : obj.name; }

export class ObjectSelector {
	
	private static selected: Selectable = null

	static get_selected() { return this.selected; }
	static is_selected(obj: Selectable) { return this.selected == obj; }

	static async select_camera(ev: PointerEvent | MouseEvent, cam: CameraObject, source: SelectSource) {
		if (this.is_selected(cam)) return;
		this.deselect(ev, 'select');

		if (PlacementRuleManager.on_select(ev, cam)) return;
		console.log(ev, cam, source)

		this.selected = cam;
		cam.list_el.classList.toggle("active", true);
		let obj = await cam.get_obj();
	}

	static async select_tag(ev: PointerEvent | MouseEvent, tag: TagObject, source: SelectSource) {
		if (this.is_selected(tag)) return;
		this.deselect(ev, 'select');

		if (PlacementRuleManager.on_select(ev, tag)) return;
		console.log(ev, tag, source)
		
		this.selected = tag;
		tag.list_el.classList.toggle("active", true);
	}

	static async select_found_tag(ev: PointerEvent | MouseEvent, tag: FoundTagObject, source: SelectSource) {
		if (this.is_selected(tag)) return;
		this.deselect(ev, 'select');

		if (PlacementRuleManager.on_select(ev, tag)) return;
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