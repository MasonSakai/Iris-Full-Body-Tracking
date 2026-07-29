import * as THREE from 'three'


//export function createMatrixT(transform: number[] | number[][]): THREE.Matrix4 {
//	if (transform == null) return null;

//	transform = transform.flat()

//	return new THREE.Matrix4(
//		 transform[ 0], -transform[ 1], -transform[ 2],  transform[ 3],
//		-transform[ 4],  transform[ 5],  transform[ 6], -transform[ 7],
//		-transform[ 8],  transform[ 9],  transform[10], -transform[11],
//		 transform[12],  transform[13],  transform[14],  transform[15]
//	)
//}

export function jsonifyMatrix(mat: THREE.Matrix4 | null): number[][] | null {
    if (mat == null) return null;
    const e = mat.elements;
    return [
        [e[0], e[4], e[ 8], e[12]],
        [e[1], e[5], e[ 9], e[13]],
        [e[2], e[6], e[10], e[14]],
        [e[3], e[7], e[11], e[15]]
    ];
}

export function CreateMatrix(transform: number[][] | number[] | null): THREE.Matrix4 | null {
	if (transform == null) return null;
	return new THREE.Matrix4().fromArray(transform.flat()).transpose();
}

export function CorrectMatrix(mat: THREE.Matrix4): THREE.Matrix4 {
    const corrective = new THREE.Matrix4().set(
        1, 0, 0, 0,
        0, -1, 0, 0,
        0, 0, -1, 0,
        0, 0, 0, 1
    );
    return new THREE.Matrix4().multiplyMatrices(corrective, mat);
}

export const DEG_TO_RAD = Math.PI / 180;

export function yawPitchToOpenCVVector(yaw: number, pitch: number) {
    const cp = Math.cos(pitch);
    const sp = Math.sin(pitch);
    const cy = Math.cos(yaw);
    const sy = Math.sin(yaw);

    // OpenCV coordinates: X = right, Y = down, Z = forward (depth)
    return new THREE.Vector3(
        cp * sy,  // X right
        -sp,      // Y down
        cp * cy   // Z forward
    );
}

export function mapRecord<K extends string | number | symbol, V, NewV>(
    record: Record<K, V>,
    callback: (value: V, key: K) => NewV
): Record<K, NewV> {
    return Object.entries(record).reduce((acc, [key, value]) => {
        acc[key as K] = callback(value as V, key as K);
        return acc;
    }, {} as Record<K, NewV>);
}
