import { Dispatch, SetStateAction, useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import { CardHandler } from "@app/ui/card_handler";
import { ConnectedComponent, LocalizationResults } from "@app/ui/solver"

function ComponentList({
    comp
}: {
        comp: ConnectedComponent
}) {
    return (
        <li>
            <button className={`dropdown-item ${CardHandler.isShowing(comp) ? 'active' : ''}`} type="button"
                onClick={() => CardHandler.open({
                    icon: null, title: `Optimization Result - ${comp.get_name()}`,
                    onRename: null, onConfirm: null, onDismiss: null,
                    content: null, source: comp
                })}
            >
                {comp.get_name()}
            </button>
        </li>
    );
}

function RelativeList() {
    if (!LocalizationResults.LatestResult) return null;
    return Object.entries(LocalizationResults.LatestResult.traversal.components)
        .sort(([a_i, a_c], [b_i, b_c]) => (b_c.members.size() - a_c.members.size()) * 100 - (a_c.id - b_c.id))
        .map(([id, comp]) => <ComponentList key={comp.id} comp={comp} />)
            
}

function SolverResults() {
    const [, forceUpdate] = useState(0);

    useEffect(() => {
        return CardHandler.ChangeListener.subscribe(() => {
            forceUpdate(v => v + 1);
        });
    }, []);

    useEffect(() => {
        return LocalizationResults.ResultListener.subscribe(() => {
            forceUpdate(v => v + 1);
        });
    }, []);

    return (
        <>
            <li className="btn btn-outline-secondary list-group-item list-group-item-light" tabIndex={0} role="button"
                data-bs-toggle="tooltip" data-bs-title="Attempts to solve for tag and camera positions using detections and placement rules"
                onClick={() => LocalizationResults.RequestLocalization()}
            >
                Localize
            </li>
            <li className={`list-group-item p-0 ${LocalizationResults.LatestResult ? '' : 'invisible'}`}>
                <div className="list-group list-group-flush dropend">
                    <button type="button" className="btn btn-outline-secondary list-group-item text-start dropdown-toggle"
                        data-bs-toggle="dropdown" aria-expanded="false">
                        Relative Optimization
                    </button>

                    <ul className="dropdown-menu">
                        <RelativeList />
                    </ul>

                    <button className={`btn btn-outline-secondary list-group-item text-start ${CardHandler.isShowing(LocalizationResults.LatestResult?.world) ? 'active' : ''}`}
                        onClick={() => {
                        if (!LocalizationResults.LatestResult) return;
                            CardHandler.open({
                                icon: null, title: 'World Optimization Result',
                                onRename: null, onConfirm: null, onDismiss: null,
                                source: LocalizationResults.LatestResult.world, content: null
                            });
                    }}>World Optimization</button>

                    <div className="btn-group btn-group-sm">
                        <button className="rounded-0 btn btn-danger" onClick={() => LocalizationResults.clear_result()}>Clear</button>
                        <button className="rounded-0 btn btn-success" onClick={() => LocalizationResults.apply_result()}>Apply</button>
                    </div>
                </div>
            </li>
        </>
    );
}

window.addEventListener('DOMContentLoaded', () =>
    createRoot(document.getElementById('localize-result'))
        .render(
            <SolverResults />
        )
);
