
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
}


let div_localizer_result: HTMLElement = null;

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

class ConnectedComponent {
	id: number
	members: SolverSet
	root: SolverIdent
	has_detection: boolean
	has_rules: boolean
	relative_solved: boolean

	constructor(data: resp_ConnectedComponent, idents: Record<number, SolverIdent>) {
		this.id = data.id;
		this.members = new SolverSet(data.members.map((i) => idents[i]));
		this.root = idents[data.root];
		this.has_detection = data.has_detection;
		this.has_rules = data.has_rules;
		this.relative_solved = data.relative_solved;
	}
}

class OptimizationResult extends CardHolder {
	success: boolean
	iterations: number
	initial_cost: number
	final_cost: number
	initial_residual_norm: number
	final_residual_norm: number
	constraint_analysis: Record<number, ConstraintAnalysis>

	constructor(data: resp_OptimizationResult) {
		super();

		this.success = data.success;
		this.iterations = data.iterations;
		this.initial_cost = data.initial_cost;
		this.final_cost = data.final_cost;
		this.initial_residual_norm = data.initial_residual_norm;
		this.final_residual_norm = data.final_residual_norm;
		this.constraint_analysis = data.constraint_analysis;
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
				(conn) => new ConnectedComponent(conn, data.objects)),
			path_costs: new SolverMap(
				Object.entries(data.traversal.path_costs)
					.map(([key, value]) => [data.objects[key], value])
			)
		};

		this.relative = mapRecord(data.relative,
			(resp) => new OptimizationResult(resp)
		);

		this.world = new OptimizationResult(data.world);

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
	div_localizer_result.classList.toggle('invisible', false);

	LatestSolverResult.poses.forEach((pose, ident) => {
		ParseIdent(ident).set_transform(pose, true);
	});
}

function clear_result() {
	div_localizer_result.classList.toggle('invisible', true);
	clearLines();

	//clear card
	LatestSolverResult = null;

	camera_list.forEach((obj) => obj.clear_preview());
	tag_list.forEach((obj) => obj.clear_preview());
	found_tag_list.forEach((obj) => obj.clear_preview());
}

window.addEventListener('DOMContentLoaded', () => {

	scene.add(line_parent);

	div_localizer_result = document.getElementById('localizer-result');

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

	document.getElementById('localize-apply').addEventListener('click', () => {
		// send poses to server
		clear_result();
	});

	document.getElementById('localize-clear').addEventListener('click', () => {
		clear_result();
	});
});