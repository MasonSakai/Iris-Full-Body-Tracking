import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { Refresh } from './network';
import { resizeRendererToDisplaySize } from './util';
import { PickHelper } from './PickHelper';
export let scene = new THREE.Scene();
scene.add(new THREE.AxesHelper(1));
export let camera = new THREE.PerspectiveCamera(75, 2, 0.01, 100);
export let controls = null;
let renderer = null;
function render(time) {
    time *= 0.001; // convert time to seconds
    if (resizeRendererToDisplaySize(renderer)) {
        var canvas = renderer.domElement;
        camera.aspect = canvas.clientWidth / canvas.clientHeight;
        camera.updateProjectionMatrix();
    }
    PickHelper.pick(scene, camera, time);
    controls.update();
    renderer.render(scene, camera);
    requestAnimationFrame(render);
}
window.onload = () => {
    var canvas = document.getElementById('tag-canvas');
    camera.fov = 2 * Math.atan(canvas.clientHeight / (2 * 240.17084283097014)) * (180 / Math.PI);
    controls = new OrbitControls(camera, canvas);
    PickHelper.init(canvas);
    renderer = new THREE.WebGLRenderer({
        antialias: true,
        canvas,
        alpha: true,
        premultipliedAlpha: false
    });
    camera.position.z = -3;
    controls.update();
    Refresh();
    requestAnimationFrame(render);
};
export function LookAt(obj) {
    controls.target.copy(obj.position);
    controls.update();
}
//# sourceMappingURL=apriltag3D.js.map