
export type CameraConfig = {
	id: number,
	name: string,
	camera_id: string,
	autostart: boolean,
	confidence_threshold: number,
	flip_horizontal: boolean
}

export const DefaultConfig: CameraConfig = {
	id: -1,
	name: "",
	camera_id: "",
	autostart: false,
	confidence_threshold: 0.15,
	flip_horizontal: false
};

export async function GetConfigs(): Promise<CameraConfig[] | undefined> {
	try {
		var response = await fetch("cameras");
		return await response.json();
	} catch (err) {
		console.error(err);
		return;
	}
}

export async function NewConfig(config: CameraConfig): Promise<CameraConfig> {
	var data = await fetch(`cameras/new`, {
		method: 'POST',
		headers: {
			'Content-type': 'application/json'
		},
		body: JSON.stringify(config)
	})
	return data.json()
}

export async function UpdateConfig(config: CameraConfig): Promise<CameraConfig> {
	var data = await fetch(`cameras/${config.id}/update`, {
		method: 'POST',
		headers: {
			'Content-type': 'application/json'
		},
		body: JSON.stringify(config)
	})
	return data.json()
}