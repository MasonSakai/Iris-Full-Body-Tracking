import { CardHandler, CardHolder } from "@app/ui/card_handler";


class PlacementRule extends CardHolder {

	write_list() {

	}

	write_card(card_overlay: HTMLElement) {

	}

	get_name: () => string = () => { throw new Error("Method not implemented.") };

	confirm(): boolean {
		throw new Error("Method not implemented.");
	}

	dismiss() { }
}

export class PlacementRules {

	public static rules = [];
	protected static lbl_rules: HTMLElement;

	public static init() {
		PlacementRules.lbl_rules = document.getElementById('list-rules');
	}

}

window.addEventListener('load', PlacementRules.init);