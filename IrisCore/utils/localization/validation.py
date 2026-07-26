

from dataclasses import dataclass
from typing import Literal

from utils.localization.graph import ConnectedComponent, Graph
from utils.localization.placement_rules import PlacementRule

@dataclass
class SolverWarning:
    component: ConnectedComponent
    message: str
    severity: Literal["warning", "error"]

def validate_components(
    components: list[ConnectedComponent],
    rules: list[PlacementRule],
) -> list[SolverWarning]:
    warnings = []

    rules_by_component: dict[int, list[PlacementRule]] = {
        component.id: []
        for component in components
    }

    component_lookup = {}

    for component in components:
        for member in component.members:
            component_lookup[member] = component

    for rule in rules:
        component = component_lookup.get(rule.target)

        if component is not None:
            rules_by_component[component.id].append(rule)

    for component in components:
        component_rules = rules_by_component[component.id]

        if not component_rules:
            warnings.append(
                SolverWarning(
                    component=component,
                    severity="warning",
                    message="Component has no placement rules",
                )
            )

    return warnings

def validate_rules(
    rules: list[PlacementRule],
    graph: Graph,
) -> list[SolverWarning]:
    errors: list[SolverWarning] = []

    for rule in rules:
        if rule.target not in graph:
            errors.append(
                SolverWarning(
                    severity="warning",
                    message=f"Rule target {rule.target} not found"
                )
            )

    return errors