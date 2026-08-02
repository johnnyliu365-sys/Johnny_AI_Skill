"""LangGraph adapter for closed router decisions."""

from __future__ import annotations

from typing import Literal

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from .contracts import RouterDecision, RouterEvent, RouterModel, RouterOutcome, RouterState
from .profile import ProjectWorkflowProfile
from .router import RouterEngine


class RouterGraphState(RouterModel):
    """Graph state intentionally holds descriptors and decisions, never raw Context packets."""

    router_state: RouterState
    router_event: RouterEvent
    profile: ProjectWorkflowProfile
    decision: RouterDecision | None = None
    graph_terminal: Literal["complete", "blocked"] | None = None


def build_router_graph(
    *,
    engine: RouterEngine,
) -> CompiledStateGraph[RouterGraphState, None, RouterGraphState, RouterGraphState]:
    """Compile a graph whose branch surface is fixed to complete or blocked."""

    graph: StateGraph[RouterGraphState, None, RouterGraphState, RouterGraphState] = StateGraph(
        RouterGraphState
    )

    def decide(state: RouterGraphState) -> RouterGraphState:
        """Evaluate one pure, profile-owned routing transition."""

        decision = engine.decide(
            state=state.router_state,
            event=state.router_event,
            profile=state.profile,
        )
        return state.model_copy(update={"decision": decision})

    def select_terminal(state: RouterGraphState) -> Literal["complete", "blocked"]:
        """Prevent unbounded node names by mapping outcomes to two declared branches."""

        if state.decision is not None and state.decision.outcome is RouterOutcome.ADVANCE:
            return "complete"
        return "blocked"

    def complete(state: RouterGraphState) -> RouterGraphState:
        """Mark a legal advance decision as terminal for this graph invocation."""

        return state.model_copy(update={"graph_terminal": "complete"})

    def blocked(state: RouterGraphState) -> RouterGraphState:
        """Mark a fail-closed result as terminal for this graph invocation."""

        return state.model_copy(update={"graph_terminal": "blocked"})

    graph.add_node("decide", decide)
    graph.add_node("complete", complete)
    graph.add_node("blocked", blocked)
    graph.add_edge(START, "decide")
    graph.add_conditional_edges(
        "decide",
        select_terminal,
        {"complete": "complete", "blocked": "blocked"},
    )
    graph.add_edge("complete", END)
    graph.add_edge("blocked", END)
    return graph.compile()
