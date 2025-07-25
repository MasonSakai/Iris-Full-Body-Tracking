import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
let scene = new THREE.Scene();
let camera = new THREE.PerspectiveCamera(75, 2, 0.1, 100);
let controls = null;
let renderer = null;
function render(time) {
    time *= 0.001; // convert time to seconds
    var canvas = renderer.domElement;
    renderer.setSize(canvas.clientWidth, canvas.clientHeight, false);
    camera.aspect = canvas.clientWidth / canvas.clientHeight;
    camera.updateProjectionMatrix();
    controls.update();
    renderer.render(scene, camera);
    requestAnimationFrame(render);
}
window.onload = () => {
    var canvas = document.getElementById('tag-canvas');
    renderer = new THREE.WebGLRenderer({
        antialias: true,
        canvas,
        alpha: true,
        premultipliedAlpha: false
    });
    controls = new OrbitControls(camera, canvas);
    camera.position.z = 2;
    const geometry = new THREE.BoxGeometry(1, 1, 1);
    const material = new THREE.MeshBasicMaterial({ color: 0x44aa88 });
    let cube = new THREE.Mesh(geometry, material);
    scene.add(cube);
    requestAnimationFrame(render);
};
//# sourceMappingURL=apriltag.js.map