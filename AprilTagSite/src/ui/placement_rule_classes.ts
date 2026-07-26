import { CardHandler, CardHolder } from "@app/ui/card_handler";
import { get_name, ObjectSelector, Selectable } from "@app/ui/object_selector";
import { RuleHandler } from "@app/ui/placement_rules";

export class PlacementRule extends CardHolder {

	protected target: Selectable;

	protected list_el: HTMLElement;
	protected list_lbl: Text;
	protected list_icon: HTMLSpanElement;

	can_rename = false;

	write_list() {
		if (!this.list_el) {
			this.list_el = document.createElement('button');
			this.list_el.className = 'btn btn-outline-secondary list-group-item text-start placement-rule';

			this.list_el.addEventListener('click', () => CardHandler.RequestElement(this, { source: 'list' }));

			this.list_icon = document.createElement('span');
			this.list_icon.className = `bi ${this.card_icon} me-2`;

			this.list_lbl = document.createTextNode('null');

			this.list_el.appendChild(this.list_icon);
			this.list_el.appendChild(this.list_lbl);
		}
		this.list_lbl.textContent = this.card_name;
		return this.list_el;
	}

	on_select: (ev: PointerEvent | MouseEvent, obj: Selectable) => boolean = () => false;

	public get_target() { return this.target; }

	public jsonify(): any {

	}
}


type NormMode = 'axis' | 'angle';
type NormMode_Axis = '+x' | '-x' | '+y' | '-y' | '+z' | '-z';

export class PlacementRule_Norm extends PlacementRule {

	private mode: NormMode;
	private axis_mode: NormMode_Axis;
	private pitch: number = 0;
	private yaw: number = 0;

	constructor() {
		super();
		this.card_icon = 'bi-box-arrow-up-right';
	}

	write_card(card_overlay: HTMLElement, { ...kwargs }: { [key: string]: any } = {}) {
		let selected: Selectable;

		switch (kwargs['source']) {
			case 'new':
				selected = ObjectSelector.get_selected();
				if (selected) this.card_name = `Facing (${get_name(selected)})`;
				else this.card_name = 'Facing';
				break;
			default:
				selected = this.target;
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
					this.card_name = `Facing (${get_name(selected)})`;
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

		card_overlay.appendChild(document.createElement('hr'));

		let sel_mode: HTMLSelectElement;
		{
			let div_mode = document.createElement('div');
			div_mode.className = 'form-floating';

			sel_mode = document.createElement('select');
			sel_mode.className = 'form-select';
			sel_mode.id = 'norm-mode';

			{
				let option_axis = document.createElement('option');
				option_axis.value = 'axis';
				option_axis.text = 'Simple';
				option_axis.selected = this.mode == 'axis';
				sel_mode.appendChild(option_axis);

				let option_angle = document.createElement('option');
				option_angle.value = 'angle';
				option_angle.text = 'Angle';
				option_angle.selected = this.mode == 'angle';
				sel_mode.appendChild(option_angle);
			}

			let lbl_mode = document.createElement('label');
			lbl_mode.htmlFor = 'norm-mode';
			lbl_mode.innerText = 'Orientation Mode';

			div_mode.appendChild(sel_mode);
			div_mode.appendChild(lbl_mode);
			card_overlay.appendChild(div_mode);
		}

		let sel_axis: HTMLSelectElement;
		let num_yaw: HTMLInputElement;
		let num_pitch: HTMLInputElement;
		{
			let div_axis = document.createElement('div');
			{
				div_axis.className = 'form-floating mt-3';
				div_axis.toggleAttribute('hidden', sel_mode.value != 'axis');

				sel_axis = document.createElement('select');
				sel_axis.className = 'form-select';
				sel_axis.id = 'norm-axis';

				{
					let option_up = document.createElement('option');
					option_up.value = '-y';
					option_up.text = 'Up';
					option_up.selected = this.axis_mode == '-y';
					sel_axis.appendChild(option_up);

					let option_down = document.createElement('option');
					option_down.value = '+y';
					option_down.text = 'Down';
					option_down.selected = this.axis_mode == '+y';
					sel_axis.appendChild(option_down);

					let option_forward = document.createElement('option');
					option_forward.value = '+z';
					option_forward.text = 'Forward';
					option_forward.selected = this.axis_mode == '+z';
					sel_axis.appendChild(option_forward);

					let option_backward = document.createElement('option');
					option_backward.value = '-z';
					option_backward.text = 'Backward';
					option_backward.selected = this.axis_mode == '-z';
					sel_axis.appendChild(option_backward);

					let option_left = document.createElement('option');
					option_left.value = '-x';
					option_left.text = 'Left';
					option_left.selected = this.axis_mode == '-x';
					sel_axis.appendChild(option_left);

					let option_right = document.createElement('option');
					option_right.value = '+x';
					option_right.text = 'Right';
					option_right.selected = this.axis_mode == '+x';
					sel_axis.appendChild(option_right);
				}

				let lbl_axis = document.createElement('label');
				lbl_axis.htmlFor = 'norm-axis';
				lbl_axis.innerText = 'Facing Direction';

				div_axis.appendChild(sel_axis);
				div_axis.appendChild(lbl_axis);
				card_overlay.appendChild(div_axis);
			}

			let div_angle = document.createElement('div');
			{
				div_angle.className = 'input-group input-group-sm mt-3';
				div_angle.toggleAttribute('hidden', sel_mode.value != 'angle');

				{
					let lbl_yaw = document.createElement('label');
					lbl_yaw.className = 'input-group-text';
					lbl_yaw.htmlFor = 'norm-yaw';
					lbl_yaw.innerText = 'Yaw';

					num_yaw = document.createElement('input');
					num_yaw.className = 'form-control';
					num_yaw.id = 'norm-yaw';
					num_yaw.type = 'number';
					num_yaw.valueAsNumber = this.pitch;
					num_yaw.min = '-180';
					num_yaw.max = '180';
					num_yaw.step = 'any';

					div_angle.appendChild(lbl_yaw);
					div_angle.appendChild(num_yaw);
				}

				{
					let lbl_pitch = document.createElement('label');
					lbl_pitch.className = 'input-group-text';
					lbl_pitch.htmlFor = 'norm-pitch';
					lbl_pitch.innerText = 'Pitch';

					num_pitch = document.createElement('input');
					num_pitch.className = 'form-control';
					num_pitch.id = 'norm-pitch';
					num_pitch.type = 'number';
					num_pitch.valueAsNumber = this.yaw;
					num_pitch.min = '-90';
					num_pitch.max = '90';
					num_pitch.step = 'any';

					div_angle.appendChild(lbl_pitch);
					div_angle.appendChild(num_pitch);
				}

				card_overlay.appendChild(div_angle);
			}

			sel_mode.addEventListener('change', () => {
				div_axis.toggleAttribute('hidden', sel_mode.value != 'axis');
				div_angle.toggleAttribute('hidden', sel_mode.value != 'angle');
			});
		}


		this.confirm = () => {
			if (!selected) {

				return false;
			}

			this.target = selected;
			this.mode = sel_mode.value as NormMode;
			switch (this.mode) {
				case 'axis':
					this.axis_mode = sel_axis.value as NormMode_Axis;
					break;
				case 'angle':
					this.yaw = num_yaw.valueAsNumber;
					this.pitch = num_pitch.valueAsNumber;
					break;
			}

			// add to placement rules if new
			if (kwargs['source'] == 'new') {
				RuleHandler.add_rule(this);
			}

			this.write_list();
			return true;
		}
	}
}
