"""
Demo：State 設計 + Node 定義

對應講義：LangGraph 實戰 → State + Node

執行方式：
  python 02_graph_structure.py

需要：
  pip install langgraph
"""

from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Optional, Annotated
from operator import add


# State（使用 Annotated 累加）
class SafetyState(TypedDict):
    raw_event: str
    event_type: Optional[str]
    severity: Optional[str]
    messages: Annotated[list, add]
    status: str


# Nodes
def parse_event(state: SafetyState) -> SafetyState:
    return {
        "event_type": state["raw_event"],
        "status": "parsed",
        "messages": ["事件已解析"],
    }


def classify_event(state: SafetyState) -> SafetyState:
    high_risk = ["no_helmet", "no_safety_belt"]
    severity = "高" if state["event_type"] in high_risk else "低"
    return {
        "severity": severity,
        "messages": [f"嚴重程度：{severity}"],
    }


def send_alert(state: SafetyState) -> SafetyState:
    return {
        "status": "alerted",
        "messages": [f"告警已發送（{state['severity']}）"],
    }


if __name__ == "__main__":
    print("=== State + Node Demo ===\n")

    graph = StateGraph(SafetyState)
    graph.add_node("parse", parse_event)
    graph.add_node("classify", classify_event)
    graph.add_node("alert", send_alert)

    graph.add_edge(START, "parse")
    graph.add_edge("parse", "classify")
    graph.add_edge("classify", "alert")
    graph.add_edge("alert", END)

    app = graph.compile()
    result = app.invoke({
        "raw_event": "no_helmet",
        "status": "pending",
        "messages": [],
    })

    print(f"狀態：{result['status']}")
    print(f"嚴重程度：{result['severity']}")
    print(f"歷程：{result['messages']}")
