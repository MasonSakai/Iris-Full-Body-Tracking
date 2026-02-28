from flask import Blueprint, render_template, flash, redirect, session, url_for, jsonify, request, abort

bp_cam = Blueprint('cameras', __name__, static_folder='static', template_folder='templates', url_prefix='/cameras')

@bp_cam.route('/', methods=['GET', 'POST'])
def index(popup_contents=''):
    return render_template('cam_manager.html')

@bp_cam.route('/new', methods=['GET', 'POST'])
def new_camera():
    if request.method == 'POST':
        count = session['new_cam_count']
        count += 1
        if count > 5:
            session['new_cam_count'] = None
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    "success": True,
                    "id": count,
                    "name": "YEEEEEAAAAAHHHHH!!!"
                })
        session['new_cam_count'] = count

    else:
        session['new_cam_count'] = 0

    return render_template('_new_cam.html', count=session['new_cam_count'])

    # form = CameraForm()

    # if form.validate_on_submit():
    #     camera = Camera(
    #         name=form.name.data,
    #         ...
    #     )
    #     db.session.add(camera)
    #     db.session.commit()

    #     # If AJAX request -> return JSON
    #     if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
    #         return jsonify({
    #             "success": True,
    #             "id": camera.id,
    #             "name": camera.name
    #         })

    #     return redirect(url_for('camera_detail', id=camera.id))

    # # Partial load for modal
    # if request.args.get('partial'):
    #     return render_template('camera_form_partial.html', form=form)

    # return render_template('camera_full_page.html', form=form)