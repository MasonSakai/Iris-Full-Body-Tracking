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
            onClick={() => CardHandler.RequestElement(rule, { source: 'list' })}
        >
            <span className={`bi ${rule.card_icon} me-2`} />
            {rule.card_name}
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