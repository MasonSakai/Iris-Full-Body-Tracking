import { CardHandler } from "@app/ui/card_handler";
import { Selectable } from "@app/ui/object_selector";
import { PlacementRule, PlacementRule_Norm } from "@app/ui/placement_rule_classes";

export class PlacementRuleManager {

	public static rules = [];
	protected static lbl_rules: HTMLElement;

	protected static selected_rule: PlacementRule = null;

	public static init() {
		PlacementRuleManager.lbl_rules = document.getElementById('list-rules');

		document.getElementById('tool-norm').addEventListener('click', () => {
			PlacementRuleManager.selected_rule = new PlacementRule_Norm();
			CardHandler.RequestElement(PlacementRuleManager.selected_rule, { source: 'new' });
		});
	}


	static on_select(ev: PointerEvent | MouseEvent, obj: Selectable): boolean {
		return this.selected_rule?.on_select(ev, obj) ?? false;
	}
}

window.addEventListener('load', PlacementRuleManager.init);