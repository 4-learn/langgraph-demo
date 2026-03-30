"""
Demo：LangSmith 觀測

對應講義：LangSmith：除錯與觀測

設定環境變數後跑這支，去 LangSmith 看 trace。

執行方式：
  1. 在 .env 設定 LANGSMITH_API_KEY, LANGSMITH_TRACING=true
  2. python 06_langsmith.py

需要：
  pip install langgraph langsmith python-dotenv
"""

import os
from dotenv import load_dotenv

load_dotenv()

# 檢查 LangSmith 設定
if not os.getenv("LANGSMITH_API_KEY"):
    print("提示：未設定 LANGSMITH_API_KEY")
    print("設定後，執行過程會自動記錄到 LangSmith")
    print("沒設定也能跑，只是不會記錄\n")

if os.getenv("LANGSMITH_TRACING") == "true":
    project = os.getenv("LANGSMITH_PROJECT", "default")
    print(f"LangSmith 已啟用，project: {project}\n")

from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Optional, Annotated, Literal
from operator import add


class SafetyState(TypedDict):
    raw_event: str
    event_type: Optional[str]
    severity: Optional[str]
    messages: Annotated[list, add]
    status: str


def parse_event(state):
    return {"event_type": state["raw_event"], "status": "parsed", "messages": ["事件已解析"]}

def classify_event(state):
    high_risk = ["no_helmet", "no_safety_belt"]
    severity = "高" if state["event_type"] in high_risk else "低"
    return {"severity": severity, "messages": [f"嚴重程度：{severity}"]}

def high_handler(state):
    return {"status": "urgent", "messages": ["高風險：已通知主管"]}

def low_handler(state):
    return {"status": "logged", "messages": ["低風險：已記錄"]}

def route(state) -> Literal["high_handler", "low_handler"]:
    return "high_handler" if state["severity"] == "高" else "low_handler"


if __name__ == "__main__":
    print("=== LangSmith Demo ===")
    print("執行後到 https://smith.langchain.com 看 trace\n")

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

    for event in ["no_helmet", "no_vest"]:
        print(f"--- {event} ---")
        result = app.invoke({"raw_event": event, "status": "pending", "messages": []})
        print(f"  狀態：{result['status']}")
        print(f"  歷程：{result['messages']}\n")

    print("去 LangSmith 看 trace，應該有 2 筆 run")
