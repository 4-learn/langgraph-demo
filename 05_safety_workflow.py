"""
Demo：完整工安事件處理系統

整合所有 LangGraph 概念：
  State + Node + 條件分支 + 迴圈重試 + Human-in-the-Loop

對應講義：Workshop：完整工安事件處理系統

流程：
  parse → classify →（高風險）→ search_reg → [審核] → notify → [重試] → finish
                    →（低風險）→ log → finish

執行方式：
  python 05_safety_workflow.py

需要：
  pip install langgraph
"""

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from typing import TypedDict, Optional, Annotated, Literal
from operator import add


# === State ===

class SafetyState(TypedDict):
    raw_event: str
    event_type: Optional[str]
    severity: Optional[str]
    regulation: Optional[str]
    retry_count: int
    success: bool
    messages: Annotated[list, add]
    status: str


# === Nodes ===

def parse_event(state):
    """邏輯 Node：解析事件"""
    return {
        "event_type": state["raw_event"],
        "status": "parsed",
        "messages": ["[parse] 事件已解析"],
    }


def classify_event(state):
    """邏輯 Node：分類嚴重程度"""
    high_risk = ["no_helmet", "no_safety_belt"]
    severity = "高" if state["event_type"] in high_risk else "低"
    return {
        "severity": severity,
        "messages": [f"[classify] 嚴重程度：{severity}"],
    }


def search_regulation(state):
    """Tool Node：查法規"""
    regulations = {
        "no_helmet": "職安法第 281 條：應使勞工確實使用安全帽。",
        "no_safety_belt": "職安法第 225 條：高空作業應使用安全帶。",
    }
    reg = regulations.get(state["event_type"], "查無相關法規")
    return {
        "regulation": reg,
        "messages": [f"[search_reg] {reg}"],
    }


def send_notification(state):
    """Tool Node：發通知（模擬，第 2 次才成功）"""
    success = state["retry_count"] >= 1

    if success:
        print(f"    ✅ 第 {state['retry_count'] + 1} 次通知：成功")
        return {
            "success": True,
            "status": "notified",
            "messages": [f"[notify] 第 {state['retry_count'] + 1} 次：成功"],
        }
    else:
        print(f"    ❌ 第 {state['retry_count'] + 1} 次通知：失敗")
        return {
            "retry_count": state["retry_count"] + 1,
            "messages": [f"[notify] 第 {state['retry_count'] + 1} 次：失敗"],
        }


def log_event(state):
    """邏輯 Node：記錄低風險事件"""
    return {
        "status": "logged",
        "messages": ["[log] 低風險事件已記錄"],
    }


def finish(state):
    """邏輯 Node：完成"""
    return {
        "status": "done",
        "messages": ["[finish] 流程完成"],
    }


def error_handler(state):
    """邏輯 Node：重試失敗"""
    return {
        "status": "failed",
        "messages": ["[error] 通知失敗，轉人工處理"],
    }


# === Routers ===

def route_by_severity(state) -> Literal["search_regulation", "log_event"]:
    """高風險 → 查法規 → 通知；低風險 → 記錄"""
    return "search_regulation" if state["severity"] == "高" else "log_event"


def should_retry(state) -> Literal["retry", "done", "give_up"]:
    """通知成功/重試/放棄"""
    if state.get("success"):
        return "done"
    if state["retry_count"] >= 3:
        return "give_up"
    return "retry"


# === Build Graph ===

def build_graph(with_human_review=False):
    graph = StateGraph(SafetyState)

    # 加入所有節點
    graph.add_node("parse", parse_event)
    graph.add_node("classify", classify_event)
    graph.add_node("search_regulation", search_regulation)
    graph.add_node("send_notification", send_notification)
    graph.add_node("log_event", log_event)
    graph.add_node("finish", finish)
    graph.add_node("error_handler", error_handler)

    # 線性部分
    graph.add_edge(START, "parse")
    graph.add_edge("parse", "classify")

    # 條件分支：高/低風險
    graph.add_conditional_edges("classify", route_by_severity)

    # 高風險路線：查法規 → 通知（可重試）
    graph.add_edge("search_regulation", "send_notification")
    graph.add_conditional_edges("send_notification", should_retry, {
        "retry": "send_notification",
        "done": "finish",
        "give_up": "error_handler",
    })

    # 低風險路線：記錄 → 完成
    graph.add_edge("log_event", "finish")

    # 結束
    graph.add_edge("finish", END)
    graph.add_edge("error_handler", END)

    # 編譯
    if with_human_review:
        checkpointer = MemorySaver()
        return graph.compile(
            checkpointer=checkpointer,
            interrupt_before=["send_notification"],
        ), checkpointer
    else:
        return graph.compile(), None


# === Demo ===

def init_state(event):
    return {
        "raw_event": event,
        "status": "pending",
        "retry_count": 0,
        "success": False,
        "messages": [],
    }


if __name__ == "__main__":
    # Demo 1：不含人工審核
    print("=" * 55)
    print("  Demo 1：自動流程（不含人工審核）")
    print("=" * 55)

    app, _ = build_graph(with_human_review=False)

    for event in ["no_helmet", "no_vest"]:
        print(f"\n--- {event} ---")
        result = app.invoke(init_state(event))
        print(f"  狀態：{result['status']}")
        print(f"  歷程：")
        for msg in result["messages"]:
            print(f"    {msg}")

    # Demo 2：含人工審核
    print(f"\n{'=' * 55}")
    print("  Demo 2：含人工審核")
    print("=" * 55)

    app, checkpointer = build_graph(with_human_review=True)
    config = {"configurable": {"thread_id": "v-001"}}

    print("\n--- Step 1：執行到審核點 ---")
    result = app.invoke(init_state("no_helmet"), config=config)
    print(f"  狀態：{result['status']}")
    print(f"  歷程：{result['messages']}")
    print(f"  → 暫停中，等待主管審核...")

    print("\n--- Step 2：主管核准 ---")
    app.update_state(config, {"messages": ["[審核] 主管已核准"]})

    print("\n--- Step 3：繼續執行 ---")
    result = app.invoke(None, config=config)
    print(f"  狀態：{result['status']}")
    print(f"  歷程：")
    for msg in result["messages"]:
        print(f"    {msg}")
