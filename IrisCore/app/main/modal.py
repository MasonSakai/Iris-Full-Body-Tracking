from flask import jsonify, make_response, redirect, request, url_for


def is_modal_request():
    """
    Checks if part of an explicit modal form request
    """
    return request.headers.get('X-Requested-With') == 'XMLHttpRequest'


def modal_success(**payload):
    return jsonify(success=True, **payload)


def modal_redirect(endpoint=None, url=None, **values):
    if endpoint:
        url = url_for(endpoint, **values)

    if is_modal_request():
        response = make_response('', 204)
        response.headers['X-Modal-Redirect'] = url
        return response

    return redirect(url)


"""

HTML/JS:

Open a modal:
Modal.open('/cameras/new')
    .then(camera => {
        console.log('Created:', camera);
    });

Open nested modal inside modal:
<a href="/sites/new" data-modal>+ New Site</a>

Break out of modal: (optional/explicit, all links breakout at the moment)
<a href="/dashboard" data-full-page>Dashboard</a>

Close modal:
<button data-modal-close>Cancel</button>

"""