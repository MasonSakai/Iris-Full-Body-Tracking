import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { RefreshFoundTags, RefreshKnownTags } from './network';
import { resizeRendererToDisplaySize } from './util';
import { PickHelper } from './PickHelper';
let scene = new THREE.Scene();
let camera = new THREE.PerspectiveCamera(75, 2, 0.1, 100);
let controls = null;
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
    controls.target.setZ(-1);
    //camera.position.z = 2
    //LoadTagModel2('tag36h11', 0).then((model) => scene.add(model))
    RefreshFoundTags(scene);
    RefreshKnownTags(scene);
    requestAnimationFrame(render);
};
//# sourceMappingURL=apriltag.js.map