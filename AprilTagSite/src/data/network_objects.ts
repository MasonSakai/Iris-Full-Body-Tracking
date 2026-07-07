

export type TagIdent = string;
export type TagID = string;
export type CameraId = string;

export type CamRecord = {
	name: string,
	id: string,
	transform: number[][],
	active: string | false
}

export type TagDetails = {
	num: number,
	pos: number[],
	rot: number[],
	v_pos: number,
	v_mar: number
};

export type FoundTagDetails = TagDetails & {
	size: number
};

export type TagRecord = {
	name: string,
	size: number,
	static: boolean,
	ident: string,
	transform: number[][],
	detections: Record<CameraId, TagDetails>
};

export type FoundTagRecord = Record<CameraId, FoundTagDetails>;

export type ScanResults = {
	known: Record<TagID, TagRecord>,
	found: Record<TagIdent, FoundTagRecord>
};