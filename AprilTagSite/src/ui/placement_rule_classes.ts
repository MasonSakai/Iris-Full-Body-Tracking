import { CardHandler } from "@app/ui/card_handler";
import { ObjectSelector, Selectable } from "@app/ui/object_selector";
import { RuleHandler } from "@app/ui/placement_rules";
import { Vector3 } from "three";
import { DEG_TO_RAD, yawPitchToOpenCVVector } from "@app/util";
import { CreateIdent } from "@app/data/solver";
import { CameraObject } from "@app/data/objects";
import { ReactNode } from "react";

export function FacingCorrection(obj: Selectable) {
	return (obj instanceof CameraObject) ? 1 : -1;
}

export class PlacementRule {

	public icon: string = null;
	public name: string;

	protected target: Selectable;

	protected weight: number = 1.0;

	can_rename = false;

	on_select: (ev: PointerEvent | MouseEvent, obj: Selectable) => boolean = () => false;

	public get_target() { return this.target; }

	public jsonify(): any {
		return { target: CreateIdent(this.target), weight: this.weight }
	}

	public render({ ...kwargs }: { [key: string]: any } = {}): ReactNode {
		return null;
	}
}

type NormMode = 'axis' | 'angle';
type NormMode_Axis = '+x' | '-x' | '+y' | '-y' | '+z' | '-z';

export class PlacementRule_Norm extends PlacementRule {

	private mode: NormMode;
	private axis_mode: NormMode_Axis;
	private pitch: number = 0;
	private yaw: number = 0;

	icon = 'bi-box-arrow-up-right';

	write_card(card_overlay: HTMLElement, { ...kwargs }: { [key: string]: any } = {}) {
		let selected: Selectable;

		switch (kwargs['source']) {
			case 'new':
				selected = ObjectSelector.get_selected();
				if (selected) this.name = `Facing (${selected.get_name()})`;
				else this.name = 'Facing';
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

			if (selected) txt_target.value = selected.get_name();

			txt_target.addEventListener('focus', () => {
				this.on_select = (ev, obj) => {
					selected = obj;
					txt_target.value = selected.get_name();
					this.name = `Facing (${selected.get_name()})`;
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


		let confirm = () => {
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

			RuleHandler.notify();
			return true;
		}
	}

	private get_direction() {
		switch (this.mode) {
			case 'axis':
				switch (this.axis_mode) {
					case '+x':
						return new Vector3( 1, 0, 0);
					case '-x':
						return new Vector3(-1, 0, 0);
					case '+y':
						return new Vector3(0,  1, 0);
					case '-y':
						return new Vector3(0, -1, 0);
					case '+z':
						return new Vector3(0, 0,  1);
					case '-z':
						return new Vector3(0, 0, -1);
				}
			case 'angle':
				return yawPitchToOpenCVVector(this.yaw * DEG_TO_RAD, this.pitch * DEG_TO_RAD)
		}
	}

	public jsonify() {
		return {
			rule_type: 'facing',
			direction: this.get_direction().multiplyScalar(FacingCorrection(this.target)).toArray(),
			...super.jsonify()
		}
	}
}


type OffsetAxis = 'x' | 'y' | 'z' | 'normal';

export class PlacementRule_Offset extends PlacementRule {

	private axis: OffsetAxis;
	private distance: number = 0;

	icon = 'bi-arrow-bar-up';

	write_card(card_overlay: HTMLElement, { ...kwargs }: { [key: string]: any } = {}) {
		let selected: Selectable;

		switch (kwargs['source']) {
			case 'new':
				selected = ObjectSelector.get_selected();
				if (selected) this.name = `Offset (${selected.get_name()})`;
				else this.name = 'Offset';
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

			if (selected) txt_target.value = selected.get_name();

			txt_target.addEventListener('focus', () => {
				this.on_select = (ev, obj) => {
					selected = obj;
					txt_target.value = selected.get_name();
					this.name = `Offset (${selected.get_name()})`;
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

		let sel_axis: HTMLSelectElement;
		{
			let div_axis = document.createElement('div');
			div_axis.className = 'form-floating mt-3';

			sel_axis = document.createElement('select');
			sel_axis.className = 'form-select';
			sel_axis.id = 'offset-axis';

			{
				let option_up = document.createElement('option');
				option_up.value = 'y';
				option_up.text = 'Up';
				option_up.selected = this.axis == 'y';
				sel_axis.appendChild(option_up);

				let option_forward = document.createElement('option');
				option_forward.value = 'z';
				option_forward.text = 'Forward';
				option_forward.selected = this.axis == 'z';
				sel_axis.appendChild(option_forward);

				let option_left = document.createElement('option');
				option_left.value = 'x';
				option_left.text = 'Left';
				option_left.selected = this.axis == 'x';
				sel_axis.appendChild(option_left);

				let option_facing = document.createElement('option');
				option_facing.value = 'normal';
				option_facing.text = 'Facing';
				option_facing.selected = this.axis == 'normal';
				sel_axis.appendChild(option_facing);
			}

			let lbl_axis = document.createElement('label');
			lbl_axis.htmlFor = 'offset-dist';
			lbl_axis.innerText = 'Offset Direction';

			div_axis.appendChild(sel_axis);
			div_axis.appendChild(lbl_axis);
			card_overlay.appendChild(div_axis);
		}

		let num_dist: HTMLInputElement;
		{
			let div_dist = document.createElement('div');
			div_dist.className = 'form-floating mt-3';

			num_dist = document.createElement('input');
			num_dist.className = 'form-control';
			num_dist.id = 'offset-dist';
			num_dist.type = 'number';
			num_dist.valueAsNumber = this.distance;
			num_dist.step = 'any';

			let lbl_dist = document.createElement('label');
			lbl_dist.htmlFor = 'offset-dist';
			lbl_dist.innerText = 'Distance';

			div_dist.appendChild(num_dist);
			div_dist.appendChild(lbl_dist);
			card_overlay.appendChild(div_dist);
		}

		let confirm = () => {
			if (!selected) {
				return false;
			}

			this.target = selected;
			this.axis = sel_axis.value as OffsetAxis;
			this.distance = num_dist.valueAsNumber;

			// add to placement rules if new
			if (kwargs['source'] == 'new') {
				RuleHandler.add_rule(this);
			}

			RuleHandler.notify();
			return true;
		}
	}

	public jsonify() {
		let cor: number;
		switch (this.axis) {
			case 'y':
				cor = -1;
				break;
			case 'normal':
				cor = FacingCorrection(this.target);
				break;
			default:
				cor = 1;
		}
		return {
			rule_type: 'offset',
			axis: this.axis,
			distance: this.distance * cor,
			...super.jsonify()
		}
	}
}
