import * as THREE from 'three'

export function resizeRendererToDisplaySize(renderer) {

	const canvas = renderer.domElement;
	const width = canvas.clientWidth;
	const height = canvas.clientHeight;
	const needResize = canvas.width !== width || canvas.height !== height;
	if (needResize) {
		renderer.setSize(width, height, false);
	}
	return needResize;
}

export function transposeMatrix(matrix) {
	return matrix[0].map((_, i) => matrix.map(row => row[i]));
}

export function createMatrixTR(pose_t: number[], pose_r: number[]): THREE.Matrix4 {
	pose_t = pose_t.flat()
	pose_r = pose_r.flat()

	return new THREE.Matrix4(
		-pose_r[0],  pose_r[1],  pose_r[2], -pose_t[0],
		-pose_r[3],  pose_r[4],  pose_r[5], -pose_t[1],
		 pose_r[6], -pose_r[7], -pose_r[8],  pose_t[2],
		0, 0, 0, 1
	)
}

export function createMatrixT(transform: number[]): THREE.Matrix4 {
	transform = transform.flat()

	return new THREE.Matrix4(
		-transform[ 0],  transform[ 1],  transform[ 2], -transform[ 3],
		-transform[ 4],  transform[ 5],  transform[ 6], -transform[ 7],
		 transform[ 8], -transform[ 9], -transform[10],  transform[11],
		 transform[12],  transform[13],  transform[14],  transform[15]
	)
}