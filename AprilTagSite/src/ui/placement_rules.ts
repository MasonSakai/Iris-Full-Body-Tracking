import { CardHandler } from "@app/ui/card_handler";
import { Selectable } from "@app/ui/object_selector";
import { PlacementRule, PlacementRule_Norm } from "@app/ui/placement_rule_classes";
import { RequestLocalization } from "@app/data/solver";

export class RuleHandler {

	public static rules: PlacementRule[] = [];
	protected static lbl_rules: HTMLElement;

	protected static selected_rule: PlacementRule = null;

	public static init() {
		RuleHandler.lbl_rules = document.getElementById('list-rules');

		document.getElementById('tool-norm').addEventListener('click', () => {
			RuleHandler.selected_rule = new PlacementRule_Norm();
			CardHandler.RequestElement(RuleHandler.selected_rule, { source: 'new' });
		});

		document.getElementById('localize').addEventListener('click', () => RequestLocalization())
	}


	static on_select(ev: PointerEvent | MouseEvent, obj: Selectable): boolean {
		return this.selected_rule?.on_select(ev, obj) ?? false;
	}

	static add_rule(rule: PlacementRule) {
		RuleHandler.rules.push(rule);
		RuleHandler.refresh_list();
	}

	static refresh_list() {
		RuleHandler.lbl_rules.parentElement.querySelectorAll('placement-rule').forEach((el) => el.remove());

		RuleHandler.lbl_rules.after(...RuleHandler.rules.map((rule) => rule.write_list()));
	}

	public static get_rules() {
		return this.rules;
	}
}

window.addEventListener('load', RuleHandler.init);