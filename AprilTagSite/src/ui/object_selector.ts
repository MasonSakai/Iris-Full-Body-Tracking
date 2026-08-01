import { CameraObject, FoundTagObject, TagObject } from "@app/data/objects";
import { PickHelper } from "@app/PickHelper";
import { RuleHandler } from "@app/ui/placement_rules";
import { EventDispatcher } from "@app/EventDispatcher";


type SelectSource = 'list' | '3D';
type DeselectSource = SelectSource | 'delete' | 'select';
export type Selectable = CameraObject | TagObject | FoundTagObject;
type SelectEvent = { select: boolean, selected: Selectable, source: SelectSource | DeselectSource };

export class ObjectSelector {

	public static readonly ChangeListener = new EventDispatcher<SelectEvent>();
	
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

		ObjectSelector.ChangeListener.dispatch({ select: true, selected: cam, source: source });
	}

	static async select_tag(ev: PointerEvent | MouseEvent, tag: TagObject, source: SelectSource) {
		if (RuleHandler.on_select(ev, tag)) return;

		if (this.is_selected(tag)) return;
		this.deselect(ev, 'select');
		
		this.selected = tag;
		tag.list_el.classList.toggle("active", true);

		ObjectSelector.ChangeListener.dispatch({ select: true, selected: tag, source: source });
	}

	static async select_found_tag(ev: PointerEvent | MouseEvent, tag: FoundTagObject, source: SelectSource) {
		if (RuleHandler.on_select(ev, tag)) return;

		if (this.is_selected(tag)) return;
		this.deselect(ev, 'select');
		
		this.selected = tag;
		tag.list_el.classList.toggle("active", true);

		ObjectSelector.ChangeListener.dispatch({ select: true, selected: tag, source: source });
	}

	static async deselect(ev: PointerEvent | MouseEvent, source: DeselectSource) {
		if (this.selected) {
			this.selected.list_el.classList.toggle("active", false);
		}
		if (source == 'select') return;

		ObjectSelector.ChangeListener.dispatch({ select: false, selected: this.selected, source: source });
		this.selected = null;
	}
}



PickHelper.default_listeners.push((e) => ObjectSelector.deselect(e, '3D'));