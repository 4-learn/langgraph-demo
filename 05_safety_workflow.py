"""
Demo：完整工安事件處理 Graph

對應講義：LangGraph 實戰 → 完整範例

執行方式：
  python 05_safety_workflow.py

需要：
  pip install langgraph
"""

from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Optional, Annotated, Literal
from operator import add


class SafetyState(TypedDict):
    raw_event: str
    event_type: Optional[str]
    severity: Optional[str]
    messages: Annotated[list, add]
    retry_count: int
    status: str


def parse_event(state):
    return {"event_type": state["raw_event"], "status": "parsed", "messages": ["事件已解析"]}

def classify_event(state):
    high_risk = ["no_helmet", "no_safety_belt"]
    severity = "高" if state["event_type"] in high_risk else "低"
    return {"severity": severity, "messages": [f"嚴重程度：{severity}"]}

def high_handler(state):
    return {"status": "urgent", "messages": ["高風險處理：通知主管"]}

def low_handler(state):
    return {"status": "logged", "messages": ["低風險處理：記錄事件"]}

def route(state) -> Literal["high_handler", "low_handler"]:
    return "high_handler" if state["severity"] == "高" else "low_handler"


if __name__ == "__main__":
    print("=== 完整工安事件處理 ===")

    graph = StateGraph(SafetyState)
    graph.add_node("parse", parse_event)
    graph.add_node("classify", classify_event)
    graph.add_node("high_handler", high_handler)
    graph.add_node("low_handler", low_handler)

    graph.add_edge(START, "parse")
    graph.add_edge("parse", "classify")
    graph.add_conditional_edges("classify", route)
    graph.add_edge("high_handler", END)
    graph.add_edge("low_handler", END)

    app = graph.compile()

    events = ["no_helmet", "no_vest", "no_safety_belt", "blocked_exit"]
    for event in events:
        print(f"\n--- {event} ---")
        result = app.invoke({"raw_event": event, "status": "pending", "retry_count": 0, "messages": []})
        print(f"  狀態：{result['status']}")
        print(f"  歷程：{result['messages']}")
