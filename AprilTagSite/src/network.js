import * as THREE from 'three';
import { createMatrix } from './util';
let texLoader = new THREE.TextureLoader();
export async function LoadTagModel(ident, size = 1) {
    var geom = new THREE.PlaneGeometry(size, size);
    var tex = await texLoader.loadAsync(`tags/image/${ident}.png`);
    tex.magFilter = THREE.NearestFilter;
    var mat = new THREE.MeshBasicMaterial({ map: tex });
    mat.side = THREE.DoubleSide;
    return new THREE.Mesh(geom, mat);
}
export async function LoadTagModel2(family, id) {
    return LoadTagModel(`${family}:${id}`);
}
let FoundTagGroup = null;
export async function RefreshFoundTags(scene) {
    if (!FoundTagGroup) {
        FoundTagGroup = new THREE.Object3D();
        scene.add(FoundTagGroup);
    }
    FoundTagGroup.clear();
    var data = await (await fetch('tags/found/list')).json();
    for (const ident in data) {
        var size = data[ident].size;
        var cams = data[ident].cams;
        var model = await LoadTagModel(ident, size);
        model.add(new THREE.AxesHelper(size));
        for (const i in cams) {
            var m = model.clone(true);
            m.name = `${ident}-${cams[i].cam.id}`;
            var pose_t = cams[i].data.pose_t;
            var pose_r = cams[i].data.pose_r;
            var mat = createMatrix(pose_t, pose_r);
            m.applyMatrix4(mat);
            FoundTagGroup.add(m);
        }
    }
}
export let tag_list = {};
let TagGroup = null;
export async function RefreshKnownTags(scene) {
    var data = await (await fetch('tags/list')).json();
    if (!TagGroup) {
        TagGroup = new THREE.Object3D();
        scene.add(TagGroup);
    }
    TagGroup.clear();
    console.log(data);
}
//# sourceMappingURL=network.js.map