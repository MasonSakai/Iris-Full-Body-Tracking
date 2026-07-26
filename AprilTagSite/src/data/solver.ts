
import { clamp } from 'three/src/math/MathUtils.js';
import { CameraId } from '@app/data/network_objects';
import { CameraObject, TagDetection, TagObject, FoundTagObject, camera_list, tag_list, found_tag_list } from '@app/data/objects';
import { jsonifyMatrix } from '@app/util';
import { Selectable } from '@app/ui/object_selector';
import { RuleHandler } from '@app/ui/placement_rules';

type SolverIdent = [string, 'camera' | 'tag' | 'found' | 'pinned'];

type SolverObject = { ident: SolverIdent, previous_pose: number[][] | null, static: boolean };

export function jsonify_Ident(obj: Selectable): SolverIdent {
	switch (true) {
		case obj instanceof CameraObject:
			return [obj.id, 'camera'];
		case obj instanceof TagObject:
			return [obj.id, 'tag'];
		case obj instanceof FoundTagObject:
			return [obj.ident, 'found'];
		default:
			obj satisfies never;
	}
}

function jsonify_SolverObject(obj: Selectable) {

	let ret: SolverObject = {
		ident: jsonify_Ident(obj),
		previous_pose: null,
		static: false
	};

	switch (true) {
		case obj instanceof CameraObject:
			ret.previous_pose = jsonifyMatrix(obj.transform);
			break;
		case obj instanceof TagObject:
			ret.previous_pose = jsonifyMatrix(obj.transform);
			ret.static = obj.static;
			break;
		case obj instanceof FoundTagObject:
			break;
		default:
			obj satisfies never;
	}

	return ret;
}

type Detection = { tag: SolverIdent, camera: SolverIdent, transform: number[][], weight: number };
let weight_k = 1;

function jsonify_Detection(tag: SolverIdent, cam: CameraId, det: TagDetection): Detection {
	return {
		tag: tag,
		camera: [cam, 'camera'],
		transform: jsonifyMatrix(det.trans), // Camera -> Tag
		weight: det.num * clamp(det.v_mar / 100.0, 0.1, 1.0) / (1.0 + weight_k * det.v_pos) // Quality
	}
}


export async function RequestLocalization() {

	let detections: Detection[] = [];
	let objects: SolverObject[] = [];

	objects.push(...camera_list.values().map(jsonify_SolverObject));

	tag_list.values().forEach((tag) => {
		objects.push(jsonify_SolverObject(tag));
		detections.push(...tag.detections.entries().map(([cam, det]) => jsonify_Detection([tag.id, 'tag'], cam, det)))
	});

	found_tag_list.values().forEach((tag) => {
		objects.push(jsonify_SolverObject(tag));
		detections.push(...tag.detections.entries().map(([cam, det]) => jsonify_Detection([tag.ident, 'found'], cam, det)))
	});

	let rules = RuleHandler.jsonify();

	let resp = await (await fetch('localizer', {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify({ detections: detections, objects: objects, rules: rules })
	})).json();

	console.log(resp);
}
