import { PickHelper } from '@app/PickHelper'
import { LookAt } from '@app/apriltag'
import { TagObject, CameraObject, tag_list, camera_list } from '@app/data/objects'




//function on_tag_select(event: MouseEvent, ident: string = '') {
//	if (selected) {
//		selected.el.classList.toggle('active', false)
//		selected = null
//	}

//	if (ident in tag_list) {
//		selected = tag_list[ident]
//		selected.el.classList.toggle('active', true)

//		LookAt(selected.obj)
//	}
//	selectionChange_listeners.forEach(f => f(event))
//}

//function on_cam_select(event: MouseEvent, id: number = -1) {
//	if (selected) {
//		selected.el.classList.toggle('active', false)
//		selected = null
//	}

//	if (id in camera_list) {
//		selected = camera_list[id]
//		selected.el.classList.toggle('active', true)

//		LookAt(selected.obj)
//	}
//	selectionChange_listeners.forEach(f => f(event))
//}
//PickHelper.add_default_listener(on_tag_select)

//export let selected: TagInfo | CameraInfo = null
//export let selectionChange_listeners: ((event: MouseEvent) => void)[] = []


//let pose_obj: THREE.Object3D = null
//async function ParsePose(data) {
//	if (!pose_obj) {
//		pose_obj = new THREE.Object3D()
//		scene.add(pose_obj)
//	}

//	var m = await LoadPoseModel()

//	for (const ident in data) {

//		var model = pose_obj.getObjectByName(ident)
//		if (!model) {
//			model = m.clone()
//			model.name = ident
//			model.matrixAutoUpdate = false
//			pose_obj.add(model)
//		}
//		model.visible = true
//		model.matrixAutoUpdate = false
//		model.matrix = createMatrixT(data[ident])
//	}

//	for (const model of pose_obj.children) {
//		if (model.name in data) continue
//		model.visible = false
//	}
//}
//socket.on('pose', ParsePose)
