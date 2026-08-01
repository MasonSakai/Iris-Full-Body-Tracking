
import * as THREE from 'three'
import { Matrix4, Object3D } from 'three';
import { ConstraintAnalysis, CreateIdent, ParseIdent, RequestLocalization as FetchLocalization, resp_ConnectedComponent, resp_OptimizationResult, resp_SolverResponse, SolverIdent } from '@app/data/solver'
import { CreateMatrix, mapRecord } from '@app/util';
import { ObjectSelector, Selectable } from '@app/ui/object_selector';
import { scene } from '@app/apriltag';
import { camera_list, found_tag_list, tag_list } from '@app/data/objects';
import { EventDispatcher } from '@app/EventDispatcher';
import { CardHandler } from './card_handler';

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


let line_parent = new Object3D();
let lines: Record<number, THREE.Line[]> = {};
let line_material = new THREE.LineBasicMaterial({ color: 0xffff00 });

export class ConnectedComponent {
	result: SolverResult

	id: number
	members: SolverSet
	root: SolverIdent
	has_detection: boolean
	has_rules: boolean
	relative_solved: boolean

	constructor(result: SolverResult, data: resp_ConnectedComponent, idents: Record<number, SolverIdent>) {
		this.result = result;

		this.id = data.id;
		this.members = new SolverSet(data.members.map((i) => idents[i]));
		this.root = idents[data.root];
		this.has_detection = data.has_detection;
		this.has_rules = data.has_rules;
		this.relative_solved = data.relative_solved;
	}

	get_name() {
		let root = ParseIdent(this.root);
		let n_members = this.members.size() - 1;
		return root.get_name() + (n_members ? ` (+${n_members})` : '');
	}

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

export class OptimizationResult {
	result: SolverResult;

	success: boolean
	iterations: number
	time: number
	initial_cost: number
	final_cost: number
	initial_residual_norm: number
	final_residual_norm: number
	constraint_analysis: Record<number, ConstraintAnalysis>

	constructor(result: SolverResult, data: resp_OptimizationResult) {
		this.result = result;

		this.success = data.success;
		this.iterations = data.iterations;
		this.time = data.time;
		this.initial_cost = data.initial_cost;
		this.final_cost = data.final_cost;
		this.initial_residual_norm = data.initial_residual_norm;
		this.final_residual_norm = data.final_residual_norm;
		this.constraint_analysis = data.constraint_analysis;
	}

	write_card(card_overlay: HTMLElement, { ...kwargs }: { [key: string]: any } = {}) {

		let div_success = document.createElement('div');
		div_success.innerText =
			`${this.success ? 'Solved' : 'Failed'} in ${(this.time * 1000).toPrecision(3)}ms
			Using ${this.iterations} iterations`;
		card_overlay.appendChild(div_success);
	}
}

export class SolverResult {
	graph: SolverMap<SolverIdent[]>
	traversal: {
		roots: SolverIdent[],
		components: Record<number, ConnectedComponent>,
		path_costs: SolverMap<number>
	}
	relative: Record<number, OptimizationResult>
	world: OptimizationResult
	poses: SolverMap<Matrix4>
	time: number

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

		this.time = data.time;
	}

	async on_select(obj: Selectable) {
		LocalizationResults.clearLines();

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
		LocalizationResults.clearLines();
	}
}

export class LocalizationResults {
	
	public static LatestResult: SolverResult = null;
	public static readonly ResultListener = new EventDispatcher();

	static init() {
		scene.add(line_parent);
		ObjectSelector.ChangeListener.subscribe((ev) => {
			if (this.LatestResult) {
				if (ev.select) this.LatestResult.on_select(ev.selected);
				else this.LatestResult.on_deselect(ev.selected);
			}
		})
	}

	public static clearLines() {
		Object.entries(lines).forEach(([id, objs]) => {
			line_parent.remove(...objs);
			objs.forEach((obj) => obj.geometry.dispose());
		});
		lines = {};
	}
	
	public static async RequestLocalization() {
		let res = new SolverResult(await FetchLocalization());
		// verify?

		if (this.LatestResult) this.clear_result();

		res.poses.forEach((pose, ident) => {
			ParseIdent(ident).set_transform(pose, true);
		});

		this.LatestResult = res;

		let selected = ObjectSelector.get_selected();
		if (selected) res.on_select(selected);

		this.ResultListener.dispatch();
		return res;
	}

	public static apply_result() {
		//

		this.clear_result();
	}
	public static clear_result() {
		for (const comp of Object.values(this.LatestResult?.traversal.components ?? {}))
			if (CardHandler.isShowing(comp)) CardHandler.dismiss();
		if (CardHandler.isShowing(this.LatestResult?.world)) CardHandler.dismiss();

		this.clearLines();
		this.LatestResult = null;

		camera_list.forEach((obj) => obj.clear_preview());
		tag_list.forEach((obj) => obj.clear_preview());
		found_tag_list.forEach((obj) => obj.clear_preview());
		this.ResultListener.dispatch();
	}
}


window.addEventListener('DOMContentLoaded', () => LocalizationResults.init());