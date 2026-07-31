
import * as THREE from 'three'
import { Matrix4, Object3D } from 'three';
import { ConstraintAnalysis, CreateIdent, ParseIdent, RequestLocalization, resp_ConnectedComponent, resp_OptimizationResult, resp_SolverResponse, SolverIdent } from '@app/data/solver'
import { CreateMatrix, mapRecord } from '@app/util';
import { CardHandler, CardHolder } from '@app/ui/card_handler';
import { ObjectSelector, Selectable } from '@app/ui/object_selector';
import { scene } from '@app/apriltag';
import { camera_list, found_tag_list, tag_list } from '@app/data/objects';

class SolverMap<T> {
	private internalMap: Map<string, T>;

	private toKey(ident: SolverIdent): string {
		return JSON.stringify(ident); // Bulletproof serialization for simple values
	}

	private fromKey(str: string): SolverIdent {
		return JSON.parse(str);
	}

	constructor(entries?: readonly (readonly [SolverIdent, T])[] | null) {
		this.internalMap = new Map<string, T>(entries.map(([k, v]) => [this.toKey(k), v]));
	}

	set(key: SolverIdent, value: T): this {
		this.internalMap.set(this.toKey(key), value);
		return this;
	}

	get(key: SolverIdent): T | undefined {
		return this.internalMap.get(this.toKey(key));
	}

	has(key: SolverIdent): boolean {
		return this.internalMap.has(this.toKey(key));
	}

	forEach(callbackfn: (value: T, key: SolverIdent) => void, thisArg?: any) {
		return this.internalMap.forEach((v, k) => callbackfn(v, this.fromKey(k)), thisArg);
	}
}

class SolverSet {
	private internalSet: Set<string>;

	private toKey(ident: SolverIdent): string {
		return JSON.stringify(ident); // Bulletproof serialization for simple values
	}

	private fromKey(str: string): SolverIdent {
		return JSON.parse(str);
	}

	constructor(entries?: readonly SolverIdent[] | null) {
		this.internalSet = new Set<string>(entries.map((k) => this.toKey(k)));
	}

	add(key: SolverIdent): this {
		this.internalSet.add(this.toKey(key));
		return this;
	}

	has(key: SolverIdent): boolean {
		return this.internalSet.has(this.toKey(key));
	}

	size() {
		return this.internalSet.size;
	}
}


let div_result: HTMLDivElement;
let div_relative: HTMLDivElement;
let btn_world: HTMLButtonElement;

let line_parent = new Object3D();
let lines: Record<number, THREE.Line[]> = {};
let line_material = new THREE.LineBasicMaterial({ color: 0xffff00 });

function clearLines() {
	Object.entries(lines).forEach(([id, objs]) => {
		line_parent.remove(...objs);
		objs.forEach((obj) => obj.geometry.dispose());
	});
	lines = {};
}

class ConnectedComponent extends CardHolder {
	result: SolverResult
	el_btn: HTMLButtonElement

	id: number
	members: SolverSet
	root: SolverIdent
	has_detection: boolean
	has_rules: boolean
	relative_solved: boolean

	constructor(result: SolverResult, data: resp_ConnectedComponent, idents: Record<number, SolverIdent>) {
		super()

		this.result = result;

		this.id = data.id;
		this.members = new SolverSet(data.members.map((i) => idents[i]));
		this.root = idents[data.root];
		this.has_detection = data.has_detection;
		this.has_rules = data.has_rules;
		this.relative_solved = data.relative_solved;

		this.has_confirm = false;
		this.card_name = `Optimization Result - ${this.get_name()}`;
	}

	get_name() {
		let root = ParseIdent(this.root);
		let n_members = this.members.size() - 1;
		return root.get_name() + (n_members ? ` (+${n_members})` : '');
	}

	write_dropdown() {
		let el_li = document.createElement('li');
		let btn = document.createElement('button');
		btn.className = 'dropdown-item';
		btn.type = 'button';
		btn.innerText = this.get_name();
		btn.setAttribute('comp-id', this.id.toString());

		btn.addEventListener('click', () => {
			this.el_btn.classList.toggle('active', true);
			CardHandler.RequestElement(this);
		});

		this.el_btn = btn;
		el_li.appendChild(btn)
		return el_li;
	}

	dismiss = () => this.el_btn.classList.toggle('active', false);

	write_card(card_overlay: HTMLElement, { ...kwargs }: { [key: string]: any } = {}) {



		card_overlay.appendChild(document.createElement('hr'));
		{
			let constraint = this.result.world.constraint_analysis[this.id];

			let div_rank = document.createElement('p');
			div_rank.innerText = `Total constraints: ${constraint.total_rank}/6
			Translation: ${constraint.translation_rank}/3
			Rotation: ${constraint.rotation_rank}/3`;
			card_overlay.appendChild(div_rank);
		}

		card_overlay.appendChild(document.createElement('hr'));
		if (this.relative_solved)
			this.result.relative[this.id].write_card(card_overlay, kwargs);
		else {
			let div_rel = document.createElement('i');
			div_rel.innerText = 'No relative optimization';
			card_overlay.appendChild(div_rel);
		}

	}
}

class OptimizationResult extends CardHolder {
	result: SolverResult;

	success: boolean
	iterations: number
	initial_cost: number
	final_cost: number
	initial_residual_norm: number
	final_residual_norm: number
	constraint_analysis: Record<number, ConstraintAnalysis>

	constructor(result: SolverResult, data: resp_OptimizationResult) {
		super();
		this.has_confirm = false;
		this.card_name = 'Optimization Result';

		this.result = result;

		this.success = data.success;
		this.iterations = data.iterations;
		this.initial_cost = data.initial_cost;
		this.final_cost = data.final_cost;
		this.initial_residual_norm = data.initial_residual_norm;
		this.final_residual_norm = data.final_residual_norm;
		this.constraint_analysis = data.constraint_analysis;
	}

	write_card(card_overlay: HTMLElement, { ...kwargs }: { [key: string]: any } = {}) {
		if (kwargs['element']) {
			kwargs['element'].classList.toggle('active', true);
			this.dismiss = () => kwargs['element'].classList.toggle('active', false);
		}


	}
}

class SolverResult {
	graph: SolverMap<SolverIdent[]>
	traversal: {
		roots: SolverIdent[],
		components: Record<number, ConnectedComponent>,
		path_costs: SolverMap<number>
	}
	relative: Record<number, OptimizationResult>
	world: OptimizationResult
	poses: SolverMap<Matrix4>

	constructor(data: resp_SolverResponse) {

		this.graph = new SolverMap(Object.entries(data.graph).map(([k, v]) => [data.objects[k], v.map((i) => data.objects[i])]));

		this.traversal = {
			roots: data.traversal.roots.map((i) => data.objects[i]),
			components: mapRecord(data.traversal.components,
				(conn) => new ConnectedComponent(this, conn, data.objects)),
			path_costs: new SolverMap(
				Object.entries(data.traversal.path_costs)
					.map(([key, value]) => [data.objects[key], value])
			)
		};

		this.relative = mapRecord(data.relative,
			(resp) => new OptimizationResult(this, resp)
		);

		this.world = new OptimizationResult(this, data.world);

		this.poses = new SolverMap(
			Object.entries(data.poses)
				.map(([key, value]) => [data.objects[key], CreateMatrix(value)])
		);
	}

	async on_select(obj: Selectable) {
		clearLines();

		let ident = CreateIdent(obj);
		if (!this.graph.has(ident)) return;

		let [comp_id, comp] = Object.entries(this.traversal.components).find(([id, comp]) => comp.members.has(ident));
		if (!comp_id) return;

		lines[comp_id] = [];

		let found = new SolverSet([ident]);
		let queue = [ident];

		while (queue.length) {
			ident = queue.pop();
			obj = ParseIdent(ident);

			for (const gid of this.graph.get(ident)) {
				if (found.has(gid)) continue;
				queue.push(gid);
				found.add(gid);
				let gobj = ParseIdent(gid);

				const geometry = new THREE.BufferGeometry().setFromPoints([(await obj.get_obj()).position, (await gobj.get_obj()).position]);
				const line = new THREE.Line(geometry, line_material);
				line_parent.add(line);
				lines[comp_id].push(line);
			}
		}
	}

	on_deselect(obj: Selectable) {
		clearLines();
	}
}

export let LatestSolverResult: SolverResult = null;

function write_result(res: SolverResult) {
	div_result.classList.toggle('invisible', false);
	div_relative.replaceChildren(...Object.entries(res.traversal.components)
		.sort(([a_i, a_c], [b_i, b_c]) => (b_c.members.size() - a_c.members.size()) * 100 - (a_c.id - b_c.id))
		.map(([i, comp]) => comp.write_dropdown()));

	res.poses.forEach((pose, ident) => {
		ParseIdent(ident).set_transform(pose, true);
	});
}

function clear_result() {
	if (btn_world.classList.contains('active')) CardHandler.Dismiss();
	else if (div_relative.querySelector('.active')) CardHandler.Dismiss();

	div_result.classList.toggle('invisible', true);
	div_relative.replaceChildren();
	clearLines();

	LatestSolverResult = null;

	camera_list.forEach((obj) => obj.clear_preview());
	tag_list.forEach((obj) => obj.clear_preview());
	found_tag_list.forEach((obj) => obj.clear_preview());
}

window.addEventListener('DOMContentLoaded', () => {

	scene.add(line_parent);

	div_result = document.getElementById('localize-result') as HTMLDivElement;
	div_relative = document.getElementById('localize-relative') as HTMLDivElement;
	btn_world = document.getElementById('localize-world') as HTMLButtonElement;

	document.getElementById('localize').addEventListener('click', async () => {
		let response = new SolverResult(await RequestLocalization());
		// verify?

		if (LatestSolverResult) clear_result();

		console.log(response);

		LatestSolverResult = response;
		write_result(response);

		let selected = ObjectSelector.get_selected();
		if (selected) response.on_select(selected);
	});

	btn_world.addEventListener('click', () => {
		if (!LatestSolverResult) return;
		CardHandler.RequestElement(LatestSolverResult.world, { element: btn_world });
	});

	document.getElementById('localize-apply').addEventListener('click', () => {
		// send poses to server
		clear_result();
	});

	document.getElementById('localize-clear').addEventListener('click', () => {
		clear_result();
	});
});