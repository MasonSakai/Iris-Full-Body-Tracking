import { CameraObject, FoundTagObject, TagObject } from "@app/data/objects";
import { PickHelper } from "@app/PickHelper";
import { RuleHandler } from "@app/ui/placement_rules";
import { LatestSolverResult } from "@app/ui/solver";


type SelectSource = 'list' | '3D';
export type Selectable = CameraObject | TagObject | FoundTagObject;

export class ObjectSelector {
	
	private static selected: Selectable = null

	static get_selected() { return this.selected; }
	static is_selected(obj: Selectable) { return this.selected == obj; }

	static async select_camera(ev: PointerEvent | MouseEvent, cam: CameraObject, source: SelectSource) {
		if (RuleHandler.on_select(ev, cam)) return;

		if (this.is_selected(cam)) return;
		this.deselect(ev, 'select');

		this.selected = cam;
		cam.list_el.classList.toggle("active", true);
		let obj = await cam.get_obj();

		LatestSolverResult?.on_select(cam);
	}

	static async select_tag(ev: PointerEvent | MouseEvent, tag: TagObject, source: SelectSource) {
		if (RuleHandler.on_select(ev, tag)) return;

		if (this.is_selected(tag)) return;
		this.deselect(ev, 'select');
		
		this.selected = tag;
		tag.list_el.classList.toggle("active", true);

		LatestSolverResult?.on_select(tag);
	}

	static async select_found_tag(ev: PointerEvent | MouseEvent, tag: FoundTagObject, source: SelectSource) {
		if (RuleHandler.on_select(ev, tag)) return;

		if (this.is_selected(tag)) return;
		this.deselect(ev, 'select');
		
		this.selected = tag;
		tag.list_el.classList.toggle("active", true);

		LatestSolverResult?.on_select(tag);
	}

	static async deselect(ev: PointerEvent | MouseEvent, source: SelectSource | 'delete' | 'select') {
		if (this.selected) {
			this.selected.list_el.classList.toggle("active", false);
		}
		if (source == 'select') return;

		LatestSolverResult?.on_deselect(this.selected);
		this.selected = null;
	}
}



PickHelper.default_listeners.push((e) => ObjectSelector.deselect(e, '3D'));