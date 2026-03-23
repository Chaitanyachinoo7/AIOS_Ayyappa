from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


NodeFn = Callable[[dict], dict]


@dataclass(frozen=True)
class Node:
    name: str
    fn: NodeFn
    deps: tuple[str, ...] = ()


def run_graph(nodes: list[Node], initial_data: dict) -> dict:
    data: dict = dict(initial_data)
    executed: set[str] = set()

    by_name = {n.name: n for n in nodes}
    remaining = set(by_name.keys())

    while remaining:
        progress = False
        for node_name in list(remaining):
            node = by_name[node_name]
            if all(dep in executed for dep in node.deps):
                out = node.fn(dict(data))
                if out:
                    data.update(out)
                executed.add(node.name)
                remaining.remove(node.name)
                progress = True
        if not progress:
            raise RuntimeError(f"workflow contains a cycle or missing deps: {sorted(remaining)}")

    return data


def run_workflow(workflow_name: str, initial_data: dict) -> dict:
    if workflow_name == "content.daily_report":
        from app.workflows.content.daily_report import nodes

        return run_graph(nodes, initial_data)

    raise ValueError(f"unknown workflow: {workflow_name}")

