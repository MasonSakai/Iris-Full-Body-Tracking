
import { Matrix4 } from 'three';
import { ConstraintAnalysis, RequestLocalization, resp_ConnectedComponent, resp_OptimizationResult, resp_SolverResponse, SolverIdent } from '@app/data/solver'
import { CreateMatrix, mapRecord } from '@app/util';
import { CardHandler, CardHolder } from '@app/ui/card_handler';

let div_localizer_result: HTMLElement = null;

class ConnectedComponent {
	id: number
	members: SolverIdent[]
	root: SolverIdent
	has_detection: boolean
	has_rules: boolean
	relative_solved: boolean

	constructor(data: resp_ConnectedComponent, idents: Record<number, SolverIdent>) {
		this.id = data.id;
		this.members = data.members.map((i) => idents[i]);
		this.root = idents[data.root];
		this.has_detection = data.has_detection;
		this.has_rules = data.has_rules;
		this.relative_solved = data.relative_solved;
	}
}

class OptimizationResult {
	success: boolean
	iterations: number
	initial_cost: number
	final_cost: number
	initial_residual_norm: number
	final_residual_norm: number
	constraint_analysis: Record<number, ConstraintAnalysis>

	constructor(data: resp_OptimizationResult) {
		this.success = data.success;
		this.iterations = data.iterations;
		this.initial_cost = data.initial_cost;
		this.final_cost = data.final_cost;
		this.initial_residual_norm = data.initial_residual_norm;
		this.final_residual_norm = data.final_residual_norm;
		this.constraint_analysis = data.constraint_analysis;
	}
}

class SolverResult extends CardHolder {
	traversal: {
		roots: SolverIdent[],
		components: Record<number, ConnectedComponent>,
		path_costs: Map<SolverIdent, number>
	}
	relative: Record<number, OptimizationResult>
	world: OptimizationResult
	poses: Map<SolverIdent, Matrix4>

	constructor(data: resp_SolverResponse) {
		super();

		this.card_name = 'Localization Results';
		this.has_confirm = false;

		this.traversal = {
			roots: data.traversal.roots.map((i) => data.objects[i]),
			components: mapRecord(data.traversal.components,
				(conn) => new ConnectedComponent(conn, data.objects)),
			path_costs: new Map<SolverIdent, number>(
				Object.entries(data.traversal.path_costs)
					.map(([key, value]) => [data.objects[key], value])
			)
		};

		this.relative = mapRecord(data.relative,
			(resp) => new OptimizationResult(resp)
		);

		this.world = new OptimizationResult(data.world);

		this.poses = new Map<SolverIdent, Matrix4>(
			Object.entries(data.poses)
				.map(([key, value]) => [data.objects[key], CreateMatrix(value)])
		);
	}

	write_card(card_overlay: HTMLElement, { ...kwargs }: { [key: string]: any } = {}) {



	}
}

export let LatestSolverResult: SolverResult = null;

function write_result(res: SolverResult) {
	
}

function clear_result() {

}

window.addEventListener('DOMContentLoaded', () => {

	div_localizer_result = document.getElementById('localizer-result');

	document.getElementById('localize').addEventListener('click', async () => {
		let response = new SolverResult(await RequestLocalization());

		console.log(response);

		write_result(response);
		CardHandler.RequestElement(response);
	})
});