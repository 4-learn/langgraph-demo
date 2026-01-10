"""
條件分支與路徑選擇

學習目標：
1. Conditional Edge 基礎
2. 路由函數設計
3. 多路徑分支
4. 動態路由
"""

from typing import TypedDict, Literal, Annotated
from operator import add


def demo_conditional_concept():
    """條件分支概念"""
    print("=== 條件分支概念 ===\n")

    print("""
# 根據 State 決定下一個節點

    ┌─────────┐
    │ classify│
    └────┬────┘
         │
    ┌────▼────┐
    │  route  │  ← 條件判斷
    └────┬────┘
         │
    ┌────┼────────────┐
    │    │            │
    ▼    ▼            ▼
  high  medium       low
    │    │            │
    └────┴────────────┘
              │
    ┌────────▼────────┐
    │      END        │
    └─────────────────┘
""")


def demo_basic_conditional():
    """基本條件分支"""
    print("\n=== 基本條件分支 ===\n")

    print("""
from langgraph.graph import StateGraph, START, END

class State(TypedDict):
    input: str
    severity: str
    result: str

def classify_node(state):
    # 模擬分類
    if "urgent" in state["input"]:
        return {"severity": "high"}
    return {"severity": "low"}

def high_priority(state):
    return {"result": "緊急處理"}

def low_priority(state):
    return {"result": "一般處理"}

# 路由函數：根據 state 決定下一個節點
def route_by_severity(state) -> str:
    if state["severity"] == "high":
        return "high_priority"
    return "low_priority"

graph = StateGraph(State)

# 加入節點
graph.add_node("classify", classify_node)
graph.add_node("high_priority", high_priority)
graph.add_node("low_priority", low_priority)

# 加入條件邊
graph.add_edge(START, "classify")
graph.add_conditional_edges(
    "classify",           # 來源節點
    route_by_severity,    # 路由函數
    {                     # 路由映射
        "high_priority": "high_priority",
        "low_priority": "low_priority",
    }
)
graph.add_edge("high_priority", END)
graph.add_edge("low_priority", END)
""")

    try:
        from langgraph.graph import StateGraph, START, END

        class State(TypedDict):
            input: str
            severity: str
            result: str

        def classify_node(state):
            if "urgent" in state["input"].lower():
                return {"severity": "high"}
            return {"severity": "low"}

        def high_priority(state):
            return {"result": "🚨 緊急處理"}

        def low_priority(state):
            return {"result": "📋 一般處理"}

        def route_by_severity(state) -> str:
            return "high_priority" if state["severity"] == "high" else "low_priority"

        graph = StateGraph(State)
        graph.add_node("classify", classify_node)
        graph.add_node("high_priority", high_priority)
        graph.add_node("low_priority", low_priority)

        graph.add_edge(START, "classify")
        graph.add_conditional_edges(
            "classify",
            route_by_severity,
            {"high_priority": "high_priority", "low_priority": "low_priority"}
        )
        graph.add_edge("high_priority", END)
        graph.add_edge("low_priority", END)

        compiled = graph.compile()

        # 測試
        print("測試 1: 一般輸入")
        result = compiled.invoke({"input": "一般違規", "severity": "", "result": ""})
        print(f"  結果: {result['result']}")

        print("\n測試 2: 緊急輸入")
        result = compiled.invoke({"input": "urgent 緊急違規", "severity": "", "result": ""})
        print(f"  結果: {result['result']}")

    except ImportError:
        print("(需安裝 langgraph 才能執行)")


def demo_literal_routing():
    """使用 Literal 類型"""
    print("\n=== Literal 類型路由 ===\n")

    print("""
# 使用 Literal 提供類型提示

from typing import Literal

def route_by_severity(state) -> Literal["high", "medium", "low"]:
    severity = state["severity"]
    if severity == "high":
        return "high"
    elif severity == "medium":
        return "medium"
    return "low"

graph.add_conditional_edges(
    "classify",
    route_by_severity,
    {
        "high": "high_handler",
        "medium": "medium_handler",
        "low": "low_handler",
    }
)
""")


def demo_end_routing():
    """路由到 END"""
    print("\n=== 路由到 END ===\n")

    print("""
# 條件判斷是否結束

from langgraph.graph import END

def should_continue(state) -> Literal["continue", "end"]:
    if state["done"]:
        return "end"
    return "continue"

graph.add_conditional_edges(
    "process",
    should_continue,
    {
        "continue": "next_step",
        "end": END,  # 直接結束
    }
)
""")


def demo_multi_path():
    """多路徑分支"""
    print("\n=== 多路徑分支 ===\n")

    print("""
# 複雜的多路徑分支

class WorkflowState(TypedDict):
    violation_type: str
    zone: str
    severity: str
    result: str

def route_violation(state) -> str:
    vtype = state["violation_type"]
    zone = state["zone"]
    severity = state["severity"]

    # 高嚴重度優先
    if severity == "high":
        return "emergency"

    # 依類型路由
    if vtype == "no_helmet":
        return "ppe_handler"
    elif vtype == "blocked_exit":
        return "safety_handler"
    elif zone == "construction":
        return "construction_handler"

    return "general_handler"

graph.add_conditional_edges(
    "classify",
    route_violation,
    {
        "emergency": "emergency_node",
        "ppe_handler": "ppe_node",
        "safety_handler": "safety_node",
        "construction_handler": "construction_node",
        "general_handler": "general_node",
    }
)
""")


def demo_dynamic_routing():
    """動態路由"""
    print("\n=== 動態路由 ===\n")

    print("""
# 使用 path_map 動態決定目標節點

def dynamic_router(state) -> str:
    # 可以返回任意節點名稱
    handler = state.get("handler")
    if handler:
        return handler
    return "default"

# 不提供固定映射，讓路由函數返回的值直接作為節點名稱
graph.add_conditional_edges(
    "router",
    dynamic_router,
    # 如果不提供 path_map，需要確保返回值是有效的節點名稱或 END
)

# 或使用 __end__ 特殊值
def smart_router(state) -> str:
    if state["complete"]:
        return "__end__"  # 等同於 END
    return "next_node"
""")


def demo_error_routing():
    """錯誤路由"""
    print("\n=== 錯誤路由 ===\n")

    print("""
# 處理錯誤的路由

class State(TypedDict):
    input: str
    error: str
    retry_count: int
    result: str

def process_node(state):
    try:
        # 處理邏輯
        result = do_something(state["input"])
        return {"result": result, "error": ""}
    except Exception as e:
        return {"error": str(e)}

def route_after_process(state) -> Literal["success", "retry", "fail"]:
    if not state["error"]:
        return "success"
    if state["retry_count"] < 3:
        return "retry"
    return "fail"

def retry_node(state):
    return {"retry_count": state["retry_count"] + 1}

graph.add_conditional_edges(
    "process",
    route_after_process,
    {
        "success": "success_handler",
        "retry": "retry",
        "fail": "error_handler",
    }
)

# retry 回到 process
graph.add_edge("retry", "process")
""")


def demo_combined_example():
    """綜合範例"""
    print("\n=== 綜合範例：違規處理流程 ===\n")

    try:
        from langgraph.graph import StateGraph, START, END

        class ViolationState(TypedDict):
            violation_type: str
            severity: str
            processed: bool
            alerts_sent: Annotated[list, add]
            result: str

        def classify(state):
            """分類違規"""
            vtype = state["violation_type"]
            if vtype in ["no_helmet", "no_safety_belt"]:
                return {"severity": "high"}
            elif vtype in ["no_vest"]:
                return {"severity": "medium"}
            return {"severity": "low"}

        def handle_high(state):
            """處理高風險"""
            return {
                "alerts_sent": ["緊急告警已發送"],
                "result": "高風險違規已緊急處理"
            }

        def handle_medium(state):
            """處理中風險"""
            return {
                "alerts_sent": ["一般告警已發送"],
                "result": "中風險違規已處理"
            }

        def handle_low(state):
            """處理低風險"""
            return {
                "result": "低風險違規已記錄"
            }

        def route_by_severity(state):
            sev = state["severity"]
            if sev == "high":
                return "high"
            elif sev == "medium":
                return "medium"
            return "low"

        # 建立 Graph
        graph = StateGraph(ViolationState)

        graph.add_node("classify", classify)
        graph.add_node("high_handler", handle_high)
        graph.add_node("medium_handler", handle_medium)
        graph.add_node("low_handler", handle_low)

        graph.add_edge(START, "classify")
        graph.add_conditional_edges(
            "classify",
            route_by_severity,
            {
                "high": "high_handler",
                "medium": "medium_handler",
                "low": "low_handler"
            }
        )
        graph.add_edge("high_handler", END)
        graph.add_edge("medium_handler", END)
        graph.add_edge("low_handler", END)

        compiled = graph.compile()

        # 測試
        test_cases = [
            {"violation_type": "no_helmet"},
            {"violation_type": "no_vest"},
            {"violation_type": "other"},
        ]

        for tc in test_cases:
            result = compiled.invoke({
                **tc,
                "severity": "",
                "processed": False,
                "alerts_sent": [],
                "result": ""
            })
            print(f"違規: {tc['violation_type']}")
            print(f"  嚴重度: {result['severity']}")
            print(f"  結果: {result['result']}")
            print(f"  告警: {result['alerts_sent']}")
            print()

    except ImportError:
        print("(需安裝 langgraph 才能執行)")


# === 主程式 ===
if __name__ == "__main__":
    print("=" * 50)
    print("條件分支與路徑選擇")
    print("=" * 50)
    print()

    demo_conditional_concept()
    demo_basic_conditional()
    demo_literal_routing()
    demo_end_routing()
    demo_multi_path()
    demo_dynamic_routing()
    demo_error_routing()
    demo_combined_example()

    print("\n完成！")
