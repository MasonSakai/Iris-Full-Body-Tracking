
export class CardHolder {

	write_card(card_overlay: HTMLElement) {
		throw new Error("Method not implemented.");
	}

	card_icon: string | null = null;
	card_name: string = '';

	can_rename = false;
	rename(): boolean {
		throw new Error("Method not implemented.");
	}

	confirm(): boolean {
		throw new Error("Method not implemented.");
	}

	dismiss() {
		throw new Error("Method not implemented.");
	}
}

export class CardHandler {

	protected static card_overlay: HTMLElement;
	protected static card_body: HTMLElement;

	protected static btn_rename: HTMLButtonElement;
	protected static txt_rename: HTMLInputElement;
	protected static icn_rename: HTMLSpanElement;

	protected static active_holder: CardHolder = null;

	public static init() {
		CardHandler.card_overlay = document.getElementById('card-overlay');
		CardHandler.card_body = CardHandler.card_overlay.querySelector('.card-body');

		CardHandler.icn_rename = document.getElementById('card-icon');
		CardHandler.txt_rename = CardHandler.card_overlay.querySelector('input#card-rename');
		CardHandler.btn_rename = CardHandler.card_overlay.querySelector('button#card-rename');

		document.getElementById('card-confirm').addEventListener('click', CardHandler.Confirm);
		document.getElementById('card-dismiss').addEventListener('click', CardHandler.Dismiss);
	}

	public static RequestElement(holder: CardHolder) {
		CardHandler.Dismiss();
		CardHandler.card_overlay.hidden = false;
		CardHandler.active_holder = holder;
		CardHandler.btn_rename.hidden = !holder.can_rename;
		CardHandler.txt_rename.disabled = !holder.can_rename;
		CardHandler.txt_rename.value = holder.card_name;
		CardHandler.icn_rename.classList = holder.card_icon ? `input-group-text bi ${holder.card_icon}` : 'input-group-text';
		holder.write_card(CardHandler.card_body);
	}

	public static Confirm() {
		if (!CardHandler.active_holder || CardHandler.active_holder.confirm()) {
			CardHandler.card_overlay.hidden = true;
			CardHandler.card_body.innerHTML = '';
		}
	}
	public static Dismiss() {
		if (CardHandler.active_holder) CardHandler.active_holder.dismiss();
		CardHandler.card_overlay.hidden = true;
		CardHandler.card_body.innerHTML = '';
	}
}

window.addEventListener('load', CardHandler.init);