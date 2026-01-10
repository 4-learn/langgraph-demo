"""
工安監控工作流程範例

學習目標：
1. 完整的工安處理流程
2. 狀態管理實踐
3. 條件分支應用
4. 循環與重試
"""

from typing import TypedDict, Annotated, Literal, Optional
from operator import add
from datetime import datetime, timezone
from dataclasses import dataclass


# === State 定義 ===

class SafetyWorkflowState(TypedDict):
    # 輸入
    event: dict  # 原始事件

    # 處理過程
    classification: Optional[dict]
    severity: str
    zone: str

    # 中間狀態
    current_step: str
    retry_count: int
    errors: Annotated[list, add]

    # 結果
    alerts: Annotated[list, add]
    actions: Annotated[list, add]
    report: str


# === 模擬資料 ===

REGULATIONS = {
    "no_helmet": "職業安全衛生設施規則 第 281 條",
    "no_vest": "職業安全衛生設施規則 第 277 條",
    "no_safety_belt": "職業安全衛生設施規則 第 225 條",
}


# === Node 函數 ===

def parse_event(state: SafetyWorkflowState) -> dict:
    """解析事件"""
    event = state["event"]
    return {
        "zone": event.get("zone", "unknown"),
        "current_step": "parsed"
    }


def classify_violation(state: SafetyWorkflowState) -> dict:
    """分類違規"""
    event = state["event"]
    vtype = event.get("type", "unknown")
    confidence = event.get("confidence", 0.5)

    # 決定嚴重程度
    if vtype in ["no_helmet", "no_safety_belt"] and confidence > 0.8:
        severity = "high"
    elif vtype in ["no_vest"] or confidence > 0.6:
        severity = "medium"
    else:
        severity = "low"

    return {
        "classification": {
            "type": vtype,
            "confidence": confidence,
            "regulation": REGULATIONS.get(vtype, "")
        },
        "severity": severity,
        "current_step": "classified"
    }


def handle_high_priority(state: SafetyWorkflowState) -> dict:
    """處理高優先級違規"""
    classification = state["classification"]
    return {
        "alerts": [{
            "level": "urgent",
            "message": f"緊急：偵測到 {classification['type']}",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }],
        "actions": ["通知現場主管", "記錄違規", "發送告警"],
        "current_step": "high_handled"
    }


def handle_medium_priority(state: SafetyWorkflowState) -> dict:
    """處理中優先級違規"""
    classification = state["classification"]
    return {
        "alerts": [{
            "level": "warning",
            "message": f"警告：偵測到 {classification['type']}",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }],
        "actions": ["記錄違規", "排程檢查"],
        "current_step": "medium_handled"
    }


def handle_low_priority(state: SafetyWorkflowState) -> dict:
    """處理低優先級違規"""
    return {
        "actions": ["記錄違規"],
        "current_step": "low_handled"
    }


def generate_report(state: SafetyWorkflowState) -> dict:
    """產生報告"""
    classification = state["classification"]
    severity = state["severity"]
    zone = state["zone"]
    alerts = state.get("alerts", [])
    actions = state.get("actions", [])

    report_lines = [
        "=== 違規處理報告 ===",
        f"區域: {zone}",
        f"類型: {classification['type']}",
        f"嚴重度: {severity}",
        f"信心度: {classification['confidence']:.0%}",
        f"相關法規: {classification['regulation']}",
        "",
        f"已發送告警: {len(alerts)} 則",
        f"執行動作: {', '.join(actions)}",
    ]

    return {
        "report": "\n".join(report_lines),
        "current_step": "completed"
    }


# === 路由函數 ===

def route_by_severity(state: SafetyWorkflowState) -> Literal["high", "medium", "low"]:
    """根據嚴重度路由"""
    severity = state["severity"]
    if severity == "high":
        return "high"
    elif severity == "medium":
        return "medium"
    return "low"


# === 建立 Graph ===

def create_safety_workflow():
    """建立工安處理工作流程"""
    try:
        from langgraph.graph import StateGraph, START, END

        graph = StateGraph(SafetyWorkflowState)

        # 加入節點
        graph.add_node("parse", parse_event)
        graph.add_node("classify", classify_violation)
        graph.add_node("high_handler", handle_high_priority)
        graph.add_node("medium_handler", handle_medium_priority)
        graph.add_node("low_handler", handle_low_priority)
        graph.add_node("report", generate_report)

        # 加入邊
        graph.add_edge(START, "parse")
        graph.add_edge("parse", "classify")

        # 條件分支
        graph.add_conditional_edges(
            "classify",
            route_by_severity,
            {
                "high": "high_handler",
                "medium": "medium_handler",
                "low": "low_handler"
            }
        )

        # 所有處理器都到報告
        graph.add_edge("high_handler", "report")
        graph.add_edge("medium_handler", "report")
        graph.add_edge("low_handler", "report")
        graph.add_edge("report", END)

        return graph.compile()

    except ImportError:
        return None


# === 視覺化 ===

def print_graph_structure():
    """印出 Graph 結構"""
    print("""
工安處理工作流程圖：

    ┌─────────┐
    │  START  │
    └────┬────┘
         │
    ┌────▼────┐
    │  parse  │  解析事件
    └────┬────┘
         │
    ┌────▼────┐
    │classify │  分類違規
    └────┬────┘
         │
    ┌────▼────┐
    │  route  │  根據嚴重度路由
    └────┬────┘
         │
    ┌────┼─────────────┐
    │    │             │
    ▼    ▼             ▼
  high  medium        low
    │    │             │
    └────┴─────────────┘
              │
    ┌─────────▼─────────┐
    │      report       │  產生報告
    └─────────┬─────────┘
              │
    ┌─────────▼─────────┐
    │        END        │
    └───────────────────┘
""")


# === 主程式 ===

def main():
    print("=" * 50)
    print("工安監控工作流程範例")
    print("=" * 50)
    print()

    # 顯示 Graph 結構
    print_graph_structure()

    # 建立 workflow
    workflow = create_safety_workflow()

    if workflow is None:
        print("需安裝 langgraph: pip install langgraph")
        print("\n以下是模擬執行：")

        # 模擬執行
        test_events = [
            {"type": "no_helmet", "confidence": 0.92, "zone": "construction"},
            {"type": "no_vest", "confidence": 0.75, "zone": "entrance"},
            {"type": "unknown", "confidence": 0.45, "zone": "office"},
        ]

        for event in test_events:
            print(f"\n處理事件: {event}")
            state = {
                "event": event,
                "classification": None,
                "severity": "",
                "zone": "",
                "current_step": "",
                "retry_count": 0,
                "errors": [],
                "alerts": [],
                "actions": [],
                "report": ""
            }

            # 模擬各步驟
            state.update(parse_event(state))
            state.update(classify_violation(state))

            if state["severity"] == "high":
                state.update(handle_high_priority(state))
            elif state["severity"] == "medium":
                state.update(handle_medium_priority(state))
            else:
                state.update(handle_low_priority(state))

            state.update(generate_report(state))

            print(state["report"])

        return

    # 實際執行 LangGraph
    print("使用 LangGraph 執行：\n")

    test_events = [
        {"type": "no_helmet", "confidence": 0.92, "zone": "construction"},
        {"type": "no_vest", "confidence": 0.75, "zone": "entrance"},
        {"type": "unknown", "confidence": 0.45, "zone": "office"},
    ]

    for event in test_events:
        print(f"處理事件: {event}")
        print("-" * 40)

        initial_state = {
            "event": event,
            "classification": None,
            "severity": "",
            "zone": "",
            "current_step": "",
            "retry_count": 0,
            "errors": [],
            "alerts": [],
            "actions": [],
            "report": ""
        }

        # 執行 workflow
        result = workflow.invoke(initial_state)

        # 輸出報告
        print(result["report"])
        print()

    # 串流執行示範
    print("=" * 40)
    print("串流執行示範：")
    print("=" * 40)

    event = {"type": "no_safety_belt", "confidence": 0.88, "zone": "construction"}
    initial_state = {
        "event": event,
        "classification": None,
        "severity": "",
        "zone": "",
        "current_step": "",
        "retry_count": 0,
        "errors": [],
        "alerts": [],
        "actions": [],
        "report": ""
    }

    print(f"\n處理事件: {event}")
    print("執行步驟：")

    for output in workflow.stream(initial_state):
        for node_name, state_update in output.items():
            step = state_update.get("current_step", "")
            print(f"  [{node_name}] -> {step}")

    print("\n完成！")


if __name__ == "__main__":
    main()
