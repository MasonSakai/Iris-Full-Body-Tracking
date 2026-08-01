import { EventDispatcher } from "@app/EventDispatcher";
import { ReactNode } from "react";

export type CardDefinition = {
	title: string;
	icon?: string;

	onRename?: (name: string) => void;
	onConfirm?: () => boolean;
	onDismiss?: () => void;

	content: () => ReactNode;

	source: any;
}

export class CardHandler {

	public static readonly ChangeListener = new EventDispatcher<CardDefinition>();

	protected static active_holder: CardDefinition = null;

	public static isShowing(source: any) {
		return CardHandler.active_holder && source === CardHandler.active_holder.source;
	}

	public static open(card: CardDefinition) {
		CardHandler.active_holder?.onDismiss?.();
		CardHandler.active_holder = card;
		CardHandler.ChangeListener.dispatch(card);
	}

	public static dismiss() {
		this.active_holder?.onDismiss?.();
		this.active_holder = null;
		this.ChangeListener.dispatch(null);
	}
}