


function finishCameraCreation(camera: { id: string, name: string }) {
    window.parent.postMessage({
        type: 'camera:selected',
        payload: { id: camera.id, name: camera.name }
    }, location.origin);
}

document.getElementById("test")?.addEventListener('click', () => {
	finishCameraCreation({id: "test_id", name: "test_name"})
})