"""
State 狀態管理基礎

學習目標：
1. 理解為什麼需要狀態
2. 定義 State Schema
3. State 的讀取和更新
4. Reducer 概念
"""

from typing import TypedDict, Annotated, Sequence
from operator import add


def demo_why_state():
    """為什麼需要狀態"""
    print("=== 為什麼需要狀態 ===\n")

    print("""
# Chain 的問題：資料傳遞有限制

# Chain 方式（線性）
chain = step1 | step2 | step3
result = chain.invoke({"input": "..."})
# 每個步驟只能取得前一步的輸出

# 真實情況：需要累積資訊
# - 對話歷史
# - 中間結果
# - 錯誤計數
# - 使用者偏好

# Graph 方式：顯式狀態管理
# State 在所有節點間共享，可以：
# - 累積資訊
# - 追蹤進度
# - 實現回溯
# - 處理錯誤重試
""")


def demo_basic_state():
    """基本 State 定義"""
    print("\n=== 基本 State 定義 ===\n")

    print("""
# 使用 TypedDict 定義 State

from typing import TypedDict

class BasicState(TypedDict):
    input: str           # 用戶輸入
    output: str          # 最終輸出
    intermediate: str    # 中間結果

# 初始狀態
initial_state = {
    "input": "分析違規",
    "output": "",
    "intermediate": ""
}
""")

    # 實際示範
    class BasicState(TypedDict):
        input: str
        output: str
        intermediate: str

    state: BasicState = {
        "input": "分析違規",
        "output": "",
        "intermediate": ""
    }

    print(f"State 結構: {BasicState.__annotations__}")
    print(f"初始狀態: {state}")


def demo_state_with_lists():
    """List 型態的 State"""
    print("\n=== List 型態 State ===\n")

    print("""
# 對於 List 型態，需要指定如何更新

from typing import Annotated
from operator import add

class ChatState(TypedDict):
    messages: Annotated[list, add]  # 使用 add 來累加 list
    context: str

# 更新時會自動累加
# 舊 state: {"messages": ["hi"]}
# node 回傳: {"messages": ["hello"]}
# 新 state: {"messages": ["hi", "hello"]}  # 自動合併
""")

    # 實際示範
    class ChatState(TypedDict):
        messages: Annotated[list, add]
        context: str

    print(f"ChatState: {ChatState.__annotations__}")
    print("Annotated[list, add] 表示每次更新會將新值加到現有 list")


def demo_complex_state():
    """複雜 State 結構"""
    print("\n=== 複雜 State 結構 ===\n")

    print("""
# 工安系統的 State 範例

from typing import TypedDict, Annotated, Optional
from operator import add
from datetime import datetime

class ViolationInfo(TypedDict):
    id: str
    type: str
    severity: str
    zone: str

class SafetyState(TypedDict):
    # 輸入
    event: dict                     # 原始事件

    # 處理狀態
    violations: Annotated[list[ViolationInfo], add]  # 累積違規
    current_step: str               # 當前步驟
    retry_count: int                # 重試計數

    # 中間結果
    classification: Optional[dict]  # 分類結果
    analysis: Optional[str]         # 分析結果

    # 輸出
    alerts: Annotated[list, add]    # 累積告警
    final_report: str               # 最終報告

    # 元資料
    started_at: datetime
    errors: Annotated[list, add]    # 累積錯誤
""")

    from typing import Optional
    from datetime import datetime

    class ViolationInfo(TypedDict):
        id: str
        type: str
        severity: str

    class SafetyState(TypedDict):
        event: dict
        violations: Annotated[list, add]
        current_step: str
        classification: Optional[dict]
        alerts: Annotated[list, add]
        errors: Annotated[list, add]

    print(f"SafetyState 欄位: {list(SafetyState.__annotations__.keys())}")


def demo_state_update():
    """State 更新機制"""
    print("\n=== State 更新機制 ===\n")

    print("""
# Node 函數回傳部分 State，自動合併

def analyze_node(state: SafetyState) -> dict:
    '''分析節點：讀取 event，輸出 classification'''

    event = state["event"]  # 讀取現有 state

    # 執行分析...
    result = {"severity": "high", "type": "no_helmet"}

    # 回傳要更新的欄位（只需要回傳有變更的）
    return {
        "classification": result,
        "current_step": "analyze_complete"
    }

# Graph 會自動合併：
# new_state = {**old_state, **node_return}
# 對於 Annotated[list, add] 欄位會特殊處理

def alert_node(state: SafetyState) -> dict:
    '''告警節點：累加 alerts'''

    # 回傳的 alerts 會加到現有的 alerts list
    return {
        "alerts": [{"message": "新告警"}],  # 會累加，不是覆蓋
        "current_step": "alert_sent"
    }
""")


def demo_reducer():
    """自訂 Reducer"""
    print("\n=== 自訂 Reducer ===\n")

    print("""
# Reducer：定義如何合併新舊值

from typing import Annotated

# 內建 reducer: add（用於 list）
# messages: Annotated[list, add]

# 自訂 reducer
def keep_latest(old: str, new: str) -> str:
    '''保留最新值'''
    return new

def keep_if_empty(old: str, new: str) -> str:
    '''只在空的時候更新'''
    return old if old else new

def merge_dicts(old: dict, new: dict) -> dict:
    '''合併字典'''
    return {**old, **new}

def increment(old: int, new: int) -> int:
    '''累加數字'''
    return old + new

# 使用自訂 reducer
class CustomState(TypedDict):
    result: Annotated[str, keep_latest]
    config: Annotated[dict, merge_dicts]
    count: Annotated[int, increment]
""")

    # 實際示範
    def keep_latest(old: str, new: str) -> str:
        return new

    def increment(old: int, new: int) -> int:
        return old + new

    print("自訂 Reducer 範例：")
    print(f"  keep_latest('舊', '新') = '{keep_latest('舊', '新')}'")
    print(f"  increment(5, 3) = {increment(5, 3)}")


def demo_message_state():
    """Message State（對話用）"""
    print("\n=== Message State（對話用）===\n")

    print("""
# LangGraph 提供預設的 Message State

from langgraph.graph import MessagesState

# MessagesState 等同於：
class MessagesState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# add_messages 是特殊的 reducer，會：
# 1. 累加新訊息
# 2. 處理相同 ID 的訊息（更新而非重複）
# 3. 保持訊息順序

# 使用方式
from langgraph.graph import StateGraph, MessagesState

graph = StateGraph(MessagesState)

def chat_node(state: MessagesState):
    messages = state["messages"]
    # 處理訊息...
    return {"messages": [AIMessage(content="回應")]}
""")


# === 主程式 ===
if __name__ == "__main__":
    print("=" * 50)
    print("State 狀態管理基礎")
    print("=" * 50)
    print()

    demo_why_state()
    demo_basic_state()
    demo_state_with_lists()
    demo_complex_state()
    demo_state_update()
    demo_reducer()
    demo_message_state()

    print("\n完成！")
