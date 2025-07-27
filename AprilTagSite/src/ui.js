import { selected, socket, selectionChange_listeners, refresh_listeners } from './network';
window.addEventListener('DOMContentLoaded', () => {
    let context_selector = document.getElementById('context-selector');
    document.getElementById('set-pos')
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
        socket.emit('set-position', selected.ident, pos, context_selector.checked);
    });
    document.getElementById('lock-norm')
        .addEventListener('click', () => {
    });
    {
        var pos_x = document.getElementById('pos-x');
        var pos_y = document.getElementById('pos-y');
        var pos_z = document.getElementById('pos-z');
        pos_x.addEventListener('input', () => { if (selected != null)
            socket.emit('set-position-axis', selected.ident, 0, pos_x.valueAsNumber, context_selector.checked); });
        pos_y.addEventListener('input', () => { if (selected != null)
            socket.emit('set-position-axis', selected.ident, 1, -pos_y.valueAsNumber, context_selector.checked); });
        pos_z.addEventListener('input', () => { if (selected != null)
            socket.emit('set-position-axis', selected.ident, 2, -pos_z.valueAsNumber, context_selector.checked); });
        var refresh = () => {
            if (selected == null) {
                pos_x.value = '';
                pos_y.value = '';
                pos_z.value = '';
            }
            else {
                pos_x.valueAsNumber = parseFloat(selected.obj.position.getComponent(0).toFixed(6));
                pos_y.valueAsNumber = parseFloat(selected.obj.position.getComponent(1).toFixed(6));
                pos_z.valueAsNumber = parseFloat(selected.obj.position.getComponent(2).toFixed(6));
            }
        };
        selectionChange_listeners.push(refresh);
        refresh_listeners.push(refresh);
    }
});
//# sourceMappingURL=ui.js.map