"""
Demo：Human-in-the-Loop（人工審核）

對應講義：Human-in-the-Loop：人工審核

流程：
  parse → classify → [暫停：等主管審核] → send_alert → END

執行方式：
  python 05_human_in_the_loop.py

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
    severity: Optional[str]
    messages: Annotated[list, add]
    status: str


# === Nodes ===

def parse_event(state):
    return {
        "severity": "高" if state["raw_event"] in ["no_helmet", "no_safety_belt"] else "低",
        "status": "parsed",
        "messages": [f"事件：{state['raw_event']}"],
    }


def send_alert(state):
    print("  📨 告警已發送")
    return {
        "status": "alerted",
        "messages": ["告警已發送"],
    }


# === Router ===

def route(state) -> Literal["send_alert", "__end__"]:
    return "send_alert" if state["severity"] == "高" else "__end__"


# === Build ===

graph = StateGraph(SafetyState)
graph.add_node("parse", parse_event)
graph.add_node("send_alert", send_alert)

graph.add_edge(START, "parse")
graph.add_conditional_edges("parse", route)
graph.add_edge("send_alert", END)

# 重點：checkpointer + interrupt_before
checkpointer = MemorySaver()
app = graph.compile(
    checkpointer=checkpointer,
    interrupt_before=["send_alert"],  # 在 send_alert 之前暫停
)


# === Demo ===

if __name__ == "__main__":
    config = {"configurable": {"thread_id": "v-001"}}

    # Step 1：執行到暫停點
    print("=== Step 1：執行到暫停點 ===")
    result = app.invoke(
        {"raw_event": "no_helmet", "status": "pending", "messages": []},
        config=config,
    )
    print(f"  嚴重程度：{result['severity']}")
    print(f"  歷程：{result['messages']}")
    print(f"  → 暫停中，等待主管審核...\n")

    # Step 2：主管審核
    print("=== Step 2：主管核准 ===")
    app.update_state(config, {"messages": ["主管已核准"]})
    print("  → 已更新 State\n")

    # Step 3：繼續執行
    print("=== Step 3：繼續執行 ===")
    result = app.invoke(None, config=config)
    print(f"  狀態：{result['status']}")
    print(f"  歷程：{result['messages']}")
