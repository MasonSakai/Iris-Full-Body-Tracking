import { tag_list, camera_list, selected } from './network';
import { LookAt } from './apriltag3D';
export function UpdateFrom(srcIdent) {
    var ignore = [];
    var queue = [srcIdent];
    while (queue.length > 0) {
        srcIdent = queue.shift();
        ignore.push(srcIdent);
        if (isNaN(+srcIdent)) {
            var tag = tag_list[srcIdent];
            tag.obj.visible = true;
            var s_mat = tag.obj.matrix.clone();
            //console.log(tag.obj.name)
            for (const id in tag.cams) {
                var cam = camera_list[id];
                if (ignore.includes(cam.ident.toString()) || queue.includes(cam.ident.toString()))
                    continue;
                var mat = tag.cams[id].clone().invert();
                s_mat.decompose(cam.obj.position, cam.obj.quaternion, cam.obj.scale);
                cam.obj.updateMatrix();
                cam.obj.applyMatrix4(mat);
                cam.obj.updateMatrix();
                queue.push(id);
            }
        }
        else {
            var cam = camera_list[srcIdent];
            cam.obj.visible = true;
            var s_mat = cam.obj.matrix.clone();
            //console.log(cam.obj.name)
            for (const ident in tag_list) {
                var tag = tag_list[ident];
                if (!(cam.ident in tag.cams))
                    continue;
                if (ignore.includes(tag.ident) || queue.includes(tag.ident))
                    continue;
                var mat = tag.cams[cam.ident].clone();
                s_mat.decompose(tag.obj.position, tag.obj.quaternion, tag.obj.scale);
                tag.obj.updateMatrix();
                tag.obj.applyMatrix4(mat);
                tag.obj.updateMatrix();
                queue.push(ident);
            }
        }
    }
    ApplyConstraints();
}
let constraints = [];
export function ApplyConstraints() {
    //0 179.4 -160
    var locked_rotations = [];
    for (const i in constraints) {
        var con = constraints[i];
    }
}
window.addEventListener('DOMContentLoaded', () => {
    document.getElementById('const-set-pos')
        .addEventListener('click', () => {
        var str = prompt('x, y, z triplet (cm), space seperated, add ~ to start for relative');
        if (str === null || str.length === 0) {
            return;
        }
        var isRel = false;
        while (isNaN(parseInt(str[0], 10))) {
            isRel = isRel || (str[0] == '~');
            str = str.substring(1);
        }
        var pos = str.split(' ').map(s => parseFloat(s) / 100);
        selected.obj.position.set(pos[0], pos[1], pos[2]);
        selected.obj.updateMatrix();
        LookAt(selected.obj);
        selected.obj.matrix.clone();
        UpdateFrom(selected.ident.toString());
    });
    document.getElementById('const-lock-norm')
        .addEventListener('click', () => {
        constraints.push({
            type: 'lock-norm',
            id: selected.obj.id
        });
    });
});
//# sourceMappingURL=constraints.js.map