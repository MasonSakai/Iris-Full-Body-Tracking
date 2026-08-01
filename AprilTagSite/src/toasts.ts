import { Toast } from 'bootstrap'

type ToastWrapper = {
	toast: Toast
	el_base: HTMLDivElement
	el_body: HTMLDivElement
}

let toast_base_element: HTMLElement;

export class Toasts {

	protected static CreateElement(close_button = true) {
		let el_base = document.createElement('div');
		el_base.className = 'toast align-items-center';
		el_base.role = 'alert';
		el_base.ariaLive = 'assertive';
		el_base.ariaAtomic = 'true';

		let div_flex = document.createElement('div');
		div_flex.className = 'd-flex';

		let el_body = document.createElement('div');
		el_body.className = 'toast-body';
		div_flex.appendChild(el_body);

		if (close_button) {
			let btn_close = document.createElement('button');
			btn_close.className = 'btn-close me-2 m-auto';
			btn_close.type = 'button';
			btn_close.ariaLabel = 'Close';
			btn_close.setAttribute('data-bs-dismiss', 'toast');
			div_flex.appendChild(btn_close);
		}

		el_base.appendChild(div_flex);
		toast_base_element.prepend(el_base);
		return { el_base: el_base, el_body: el_body };
	}

	protected static reusable_toasts: Record<string, ToastWrapper> = {}

	static CreateReusableToast(id: string, message: string = null, {
		animation = true, autohide = true, delay = 5000,
		show = true, default_close = true, on_hidden = () => { }
	} = {}) {
		let { el_base: el_base, el_body: el_body } = Toasts.CreateElement(default_close);
		let toast = new Toast(el_base, { animation: animation, autohide: autohide, delay: delay });

		el_body.innerText = message;

		if (show) toast.show();
		el_base.addEventListener('hidden.bs.toast', on_hidden);

		let wrapper: ToastWrapper = { toast: toast, el_base: el_base, el_body: el_body };
		Toasts.reusable_toasts[id] = wrapper;
		return wrapper;
	}

	static GetReusableToast(id: string) {
		//if (!(id in Toasts.reusable_toasts)) return null;
		return Toasts.reusable_toasts[id];
	}

	static CreateDisposableToast(message: string = null, {
		animation = true, autohide = true, delay = 5000,
		default_close = true, on_hidden = () => { }
	} = {}): ToastWrapper {
		let { el_base: el_base, el_body: el_body } = Toasts.CreateElement(default_close);
		let toast = new Toast(el_base, { animation: animation, autohide: autohide, delay: delay });

		el_body.innerText = message;

		toast.show();
		el_base.addEventListener('hidden.bs.toast', () => {
			on_hidden();
			toast.dispose();
			el_base.remove();
		});

		return {
			toast: toast,
			el_base: el_base,
			el_body: el_body
		};
	}
}

window.addEventListener('DOMContentLoaded', () => {
	toast_base_element = document.getElementById('toasts');
})