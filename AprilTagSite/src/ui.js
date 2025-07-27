import { selected, socket } from './network';
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
        pos[1] *= -1;
        pos[2] *= -1;
        socket.emit('set-position', selected.ident, pos);
    });
    document.getElementById('const-lock-norm')
        .addEventListener('click', () => {
    });
});
//# sourceMappingURL=ui.js.map