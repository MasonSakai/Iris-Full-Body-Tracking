import { CardHandler, CardHolder } from "@app/ui/card_handler";
import { get_name, ObjectSelector, Selectable } from "@app/ui/object_selector";
import { FoundTagObject } from "@app/data/objects";

export class PlacementRule extends CardHolder {

	protected list_el: HTMLElement;

	can_rename = false;

	write_list() {
		if (!this.list_el) {
			this.list_el = document.createElement('button');
			this.list_el.className = `btn btn-outline-secondary list-group-item ${this.card_icon}`
			this.list_el.innerText = this.card_name;

			this.list_el.addEventListener('click', () => CardHandler.RequestElement(this, { source: 'list' }));
		}
		return this.list_el;
	}

	on_select: (ev: PointerEvent | MouseEvent, obj: Selectable) => boolean = () => false;
}



export class PlacementRule_Norm extends PlacementRule {

	private selected: Selectable;

	constructor() {
		super();
		this.card_icon = 'bi-box-arrow-up-right';
	}

	write_card(card_overlay: HTMLElement, { ...kwargs }: { [key: string]: any } = {}) {
		let selected: Selectable;

		switch (kwargs['source']) {
			case 'new':
				selected = ObjectSelector.get_selected();
				if (selected) {
					this.card_name = get_name(selected);
				}
				break;
			default:
				selected = this.selected;
				break;
		}

		{
			let div_target = document.createElement('div');
			div_target.className = 'form-floating';

			let txt_target = document.createElement('input');
			txt_target.className = 'form-control';
			txt_target.readOnly = true;
			txt_target.type = 'text';
			txt_target.id = 'norm-target';
			txt_target.placeholder = '';

			if (selected) txt_target.value = get_name(selected);

			txt_target.addEventListener('focus', () => {
				this.on_select = (ev, obj) => {
					selected = obj;
					txt_target.value = get_name(selected);
					this.card_name = txt_target.value;
					CardHandler.UpdateName();
					return true;
				}
			});
			txt_target.addEventListener('blur', (ev) => {
				let related = ev.relatedTarget;
				if (related instanceof HTMLElement && related.hasAttribute('keepfocus')) {
					ev.preventDefault();
					txt_target.focus();
					return;
				}
				this.on_select = () => false;
			});

			let lbl_target = document.createElement('label');
			lbl_target.htmlFor = 'norm-target';
			lbl_target.innerText = 'Select Target';

			div_target.appendChild(txt_target);
			div_target.appendChild(lbl_target);
			card_overlay.appendChild(div_target);

			if (!selected) txt_target.focus();
		}

	}
}
