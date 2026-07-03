(function () {

    const Modal = {
        stack: [],

        open(url) {
            return new Promise((resolve, reject) => {

                const dialog = document.createElement('dialog');
                dialog.className = 'app-modal';

                const content = document.createElement('div');
                content.className = 'app-modal-content';
                dialog.appendChild(content);

                document.body.appendChild(dialog);

                dialog.showModal();

                const cleanup = () => {
                    dialog.remove();
                    this.stack.pop();
                };

                dialog.addEventListener('close', () => {
                    cleanup();
                    reject('closed');
                }, { once: true });

                const load = async (url, options = {}) => {
                    const response = await fetch(url, options);

                    // Full page redirect
                    const redirectHeader = response.headers.get('X-Modal-Redirect');
                    if (redirectHeader) {
                        window.location.href = redirectHeader;
                        return;
                    }

                    const contentType = response.headers.get('content-type') || '';

                    // Success JSON
                    if (contentType.includes('application/json')) {
                        const data = await response.json();

                        if (data.redirect) {
                            window.location.href = data.redirect;
                            return;
                        }

                        if (data.success) {
                            dialog.close();
                            resolve(data);
                            return;
                        }
                    }

                    // Otherwise HTML
                    const html = await response.text();

                    // Safety fallback: full layout accidentally returned
                    if (html.includes('<html')) {
                        window.location.href = url;
                        return;
                    }

                    content.innerHTML = html;
                    wire(content);
                };

                const wire = (container) => {

                    // Intercept forms
                    container.querySelectorAll('form').forEach(form => {
                        form.addEventListener('submit', async (e) => {
                            e.preventDefault();

                            const formData = new FormData(form);

                            await load(form.action, {
                                method: form.method || 'POST',
                                body: formData,
                                headers: {
                                    'X-Requested-With': 'XMLHttpRequest'
                                }
                            });
                        });
                    });

                    // Links that open another modal
                    container.querySelectorAll('[data-modal]').forEach(link => {
                        link.addEventListener('click', async (e) => {
                            e.preventDefault();
                            await load(link.href, {
                                method: link.method || 'GET',
                                headers: {
                                    'X-Requested-With': 'XMLHttpRequest'
                                }
                            });
                        });
                    });

                    // Links that open another modal
                    container.querySelectorAll('[data-modal-new]').forEach(link => {
                        link.addEventListener('click', (e) => {
                            e.preventDefault();
                            Modal.open(link.href).catch(() => { });
                        });
                    });

                    // Links that break out to full page
                    container.querySelectorAll('[data-full-page]').forEach(link => {
                        link.addEventListener('click', (e) => {
                            e.preventDefault();
                            window.location.href = link.href;
                        });
                    });

                    // Cancel buttons
                    container.querySelectorAll('[data-modal-close]').forEach(btn => {
                        btn.addEventListener('click', () => {
                            dialog.close();
                        });
                    });
                };

                this.stack.push({ el: dialog, load: load });
                load(url);
            });
        },

        register(link, event = 'click') {
            link.addEventListener(event, (e) => {
                e.preventDefault();
                Modal.open(link.href || link.getAttribute('href'))
                    .then(() => {
                        if (link.hasAttribute('data-modal-refresh') || link.hasAttribute('data-modal-refresh-always')) {
                            window.location.href = window.location.href;
                        }
                    })
                    .catch(() => {
                        if (link.hasAttribute('data-modal-refresh-always')) {
                            window.location.href = window.location.href;
                        }
                    });
            });
        }
    };

    window.Modal = Modal;
    window.addEventListener('load', () => {
        document.querySelectorAll('[data-modal-new]').forEach((el) => Modal.register(el));
    });

})();