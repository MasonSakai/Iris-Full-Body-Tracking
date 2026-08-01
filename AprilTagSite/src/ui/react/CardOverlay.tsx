import { useEffect, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import { CardDefinition, CardHandler } from "@app/ui/card_handler";

function CardOverlay() {

	const [card, cardUpdate] = useState<CardDefinition | null>(null);
	const [name, nameUpdate] = useState("");
	const txtName = useRef<HTMLInputElement>(null);

	useEffect(() => {
		return CardHandler.ChangeListener.subscribe((newCard) => {
			cardUpdate(newCard);
		});
	}, []);

	useEffect(() => {
		if (card)
			nameUpdate(card.title);
	}, [card]);

	if (!card) return null;

	return (
		<div className="card bg-body-secondary">
			<div className="card-header input-group input-group-sm p-0">
				{card.icon && <i className={`input-group-text bi ${card.icon}`} />}
				<input type="text" aria-label="Rename" className="form-control"
					ref={txtName} value={name} disabled={!card.onRename}
					onChange={(ev) => { }}
				/>
				{card.onRename && <button className="btn btn-outline-secondary bi bi-pencil-square" onClick={() => {
					card.onRename(txtName.current.value); nameUpdate(card.title);
				}} />}
				{card.onConfirm && <button className="btn btn-outline-success bi bi-check-lg" onClick={() => {
					card.onConfirm() && CardHandler.dismiss()
				}} />}
				<button className="btn btn-outline-danger bi bi-x-lg" onClick={() => CardHandler.dismiss()} />
			</div>
			<div className="card-body">{card.content?.()}</div>
		</div>
	);
}

window.addEventListener('DOMContentLoaded', () =>
	createRoot(document.getElementById('card-overlay'))
		.render(
			<CardOverlay />
		)
);