from langgraph.graph import StateGraph, START, END
from state import SupervisorState
from agents import regulation_agent, report_agent, notification_agent


def supervisor_decide(state: SupervisorState) -> dict:
    """Supervisor：決定下一步要交給誰"""
    completed = state.get("completed_agents", [])

    if "regulation" not in completed:
        next_agent = "regulation"
    elif "report" not in completed:
        next_agent = "report"
    elif "notification" not in completed:
        next_agent = "notification"
    else:
        next_agent = "done"

    return {
        "next_agent": next_agent,
        "messages": [f"🎯 Supervisor 決策：下一步 → {next_agent}"],
    }


def route_to_agent(state: SupervisorState) -> str:
    """Conditional Edge：根據 Supervisor 決策路由"""
    return state["next_agent"]


graph = StateGraph(SupervisorState)

graph.add_node("supervisor", supervisor_decide)
graph.add_node("regulation", regulation_agent)
graph.add_node("report", report_agent)
graph.add_node("notification", notification_agent)

graph.add_edge(START, "supervisor")

graph.add_conditional_edges(
    "supervisor",
    route_to_agent,
    {
        "regulation": "regulation",
        "report": "report",
        "notification": "notification",
        "done": END,
    },
)

graph.add_edge("regulation", "supervisor")
graph.add_edge("report", "supervisor")
graph.add_edge("notification", "supervisor")

app = graph.compile()
