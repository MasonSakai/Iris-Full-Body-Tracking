from flask import jsonify, make_response, redirect, request, url_for


def is_modal_request():
    """
    Checks if part of an explicit modal form request
    """
    return request.headers.get('X-Requested-With') == 'XMLHttpRequest'


def modal_success(**payload):
    return jsonify(success=True, **payload)


def modal_redirect(endpoint=None, url=None, **values):
    """
    Redirects with modal escape
    DOES NOT REDIRECT MODAL ITSELF (if is_modal_request)
    """
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

Navigate inside modal:
<a href="/sites/next" data-modal>Next Site</a>

Open nested modal inside modal:
<a href="/sites/new" data-modal-new>+ New Site</a>

Break out of modal: (optional/explicit, all links breakout at the moment)
<a href="/dashboard" data-full-page>Dashboard</a>

Close modal (counts as failure):
<button data-modal-close>Cancel</button>

Refresh page (base layer only, always will refresh on failure/cancel):
<a href="/sites/new" data-modal-new data-modal-refresh>+ New Site</a>
<a href="/sites/new" data-modal-new data-modal-refresh-always>+ New Site</a>

"""