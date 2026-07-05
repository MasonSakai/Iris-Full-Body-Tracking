

export type TagIdent = string;
export type FoundTagIdent = string;
export type CameraIdent = string;

export type TagDetails = {
	num: number,
	pos: number[],
	rot: number[][],
	v_pos: number,
	v_mar: number
};

export type FoundTagDetails = TagDetails & {
	size: number
};


export type ScanResults = {
	known: {
		[ident: TagIdent]: {
			name: string,
			size: number,
			cams: Record<CameraIdent, TagDetails>
		}
	},
	found: Record<FoundTagIdent, Record<CameraIdent, FoundTagDetails>>
};