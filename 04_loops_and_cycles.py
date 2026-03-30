"""
Demo：迴圈重試

對應講義：LangGraph 實戰 → 迴圈

執行方式：
  python 04_loops_and_cycles.py

需要：
  pip install langgraph
"""

from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated, Literal
from operator import add
import random


class RetryState(TypedDict):
    task: str
    retry_count: int
    success: bool
    messages: Annotated[list, add]
    status: str


def send_notification(state):
    """模擬發送通知（30% 機率失敗）"""
    random.seed(state["retry_count"])
    success = state["retry_count"] >= 2  # 第 3 次才成功

    if success:
        print(f"  ✅ 第 {state['retry_count'] + 1} 次：發送成功")
        return {"success": True, "status": "notified", "messages": ["通知已發送"]}
    else:
        print(f"  ❌ 第 {state['retry_count'] + 1} 次：發送失敗")
        return {
            "retry_count": state["retry_count"] + 1,
            "messages": [f"第 {state['retry_count'] + 1} 次失敗"],
        }


def finish(state):
    return {"status": "done", "messages": ["流程完成"]}


def error_handler(state):
    return {"status": "failed", "messages": ["超過重試次數，轉人工處理"]}


# Router
def should_retry(state) -> Literal["retry", "done", "give_up"]:
    if state.get("success"):
        return "done"
    if state["retry_count"] >= 3:
        return "give_up"
    return "retry"


if __name__ == "__main__":
    print("=== 迴圈重試 Demo ===\n")

    graph = StateGraph(RetryState)
    graph.add_node("send", send_notification)
    graph.add_node("finish", finish)
    graph.add_node("error", error_handler)

    graph.add_edge(START, "send")
    graph.add_conditional_edges("send", should_retry, {
        "retry": "send",
        "done": "finish",
        "give_up": "error",
    })
    graph.add_edge("finish", END)
    graph.add_edge("error", END)

    app = graph.compile()
    result = app.invoke({
        "task": "發送告警通知",
        "retry_count": 0,
        "success": False,
        "messages": [],
        "status": "pending",
    })

    print(f"\n最終狀態：{result['status']}")
    print(f"歷程：{result['messages']}")
