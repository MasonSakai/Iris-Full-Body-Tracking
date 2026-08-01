import { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import { CardHandler } from "@app/ui/card_handler";
import { PlacementRule } from "@app/ui/placement_rule_classes";
import { RuleHandler } from "@app/ui/placement_rules";

function RuleButton({
    rule
}: {
    rule: PlacementRule;
}) {
    return (
        <button
            className="btn btn-outline-secondary list-group-item text-start"
            onClick={() => CardHandler.open({
                icon: rule.icon, title: rule.name,
                onRename: null, onDismiss: null,
                onConfirm: null,
                content: null,
                source: rule
            })} //rule, { source: 'list' }
        >
            <span className={`bi ${rule.icon} me-2`} />
            {rule.name}
        </button>
    );
}

function RuleList() {
    const [, forceUpdate] = useState(0);

    useEffect(() => {
        return RuleHandler.subscribe(() => {
            forceUpdate(v => v + 1);
        });
    }, []);

    return (
        <>
            {RuleHandler.getRules().map((rule, i) =>
                <RuleButton
                    key={i}
                    rule={rule}
                />
            )}
        </>
    );
}

window.addEventListener('DOMContentLoaded', () =>
    createRoot(document.getElementById('list-rules'))
        .render(
            <RuleList />
        )
);