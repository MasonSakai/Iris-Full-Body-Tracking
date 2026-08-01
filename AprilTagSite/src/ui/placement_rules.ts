import { CardHandler } from "@app/ui/card_handler";
import { Selectable } from "@app/ui/object_selector";
import { PlacementRule, PlacementRule_Norm, PlacementRule_Offset } from "@app/ui/placement_rule_classes";

export class RuleHandler {
	private static rules: PlacementRule[] = [];

	public static getRules(): readonly PlacementRule[] {
		return this.rules;
	}

	protected static selected_rule: PlacementRule = null;

	public static init() {

		//document.getElementById('tool-norm').addEventListener('click', () => {
		//	RuleHandler.selected_rule = new PlacementRule_Norm();
		//	CardHandler.RequestElement(RuleHandler.selected_rule, { source: 'new' });
		//});

		//document.getElementById('tool-offset').addEventListener('click', () => {
		//	RuleHandler.selected_rule = new PlacementRule_Offset();
		//	CardHandler.RequestElement(RuleHandler.selected_rule, { source: 'new' });
		//});
	}


	static on_select(ev: PointerEvent | MouseEvent, obj: Selectable): boolean {
		return this.selected_rule?.on_select(ev, obj) ?? false;
	}


	private static listeners = new Set<() => void>();

	static subscribe(listener: () => void) {
		this.listeners.add(listener);
		return () => { this.listeners.delete(listener) };
	}

	public static notify() {
		this.listeners.forEach(l => l());
	}

	static add_rule(rule: PlacementRule) {
		RuleHandler.rules.push(rule);
		RuleHandler.notify();
	}

	public static jsonify() {
		return this.rules.map((rule) => rule.jsonify());
	}
}

window.addEventListener('DOMContentLoaded', RuleHandler.init);