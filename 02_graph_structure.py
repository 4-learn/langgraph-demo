"""
Demo：State 設計 + 三種 Node

對應講義：LangGraph 實戰 → State + Node（三種常見 Node）

執行方式：
  python 02_graph_structure.py

需要：
  pip install langgraph langchain-google-genai python-dotenv
  .env 裡設定 GOOGLE_API_KEY（Demo 2 需要）
"""

import os
from dotenv import load_dotenv

load_dotenv()

from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Optional, Annotated
from operator import add


# === State ===

class SafetyState(TypedDict):
    raw_event: str
    event_type: Optional[str]
    severity: Optional[str]
    regulation: Optional[str]
    messages: Annotated[list, add]
    status: str


# === 三種 Node ===

# 1. 邏輯 Node（純 Python）
def parse_event(state: SafetyState) -> SafetyState:
    """解析事件——不需要 LLM，純邏輯"""
    return {
        "event_type": state["raw_event"],
        "status": "parsed",
        "messages": ["[邏輯 Node] 事件已解析"],
    }


def classify_event(state: SafetyState) -> SafetyState:
    """分類嚴重程度——規則判斷，不需要 LLM"""
    high_risk = ["no_helmet", "no_safety_belt"]
    severity = "高" if state["event_type"] in high_risk else "低"
    return {
        "severity": severity,
        "messages": [f"[邏輯 Node] 嚴重程度：{severity}"],
    }


# 2. LLM Node（呼叫 Gemini）
def analyze_with_llm(state: SafetyState) -> SafetyState:
    """用 LLM 分析——需要語意理解的任務"""
    from langchain_google_genai import ChatGoogleGenerativeAI

    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
    response = llm.invoke(
        f"用一句話描述這個工安違規的風險：{state['event_type']}"
    )
    return {
        "messages": [f"[LLM Node] {response.content[:80]}"],
    }


# 3. Tool Node（呼叫外部系統）
def search_regulation(state: SafetyState) -> SafetyState:
    """查詢法規——呼叫外部資料庫"""
    regulations = {
        "no_helmet": "職安法第 281 條：應使勞工確實使用安全帽。",
        "no_safety_belt": "職安法第 225 條：高空作業應使用安全帶。",
    }
    reg = regulations.get(state["event_type"], "查無相關法規")
    return {
        "regulation": reg,
        "messages": [f"[Tool Node] 法規：{reg}"],
    }


# === Demo 1：邏輯 Node（不需要 API Key） ===

def demo_logic_nodes():
    print("=== Demo 1：邏輯 Node ===\n")

    graph = StateGraph(SafetyState)
    graph.add_node("parse", parse_event)
    graph.add_node("classify", classify_event)

    graph.add_edge(START, "parse")
    graph.add_edge("parse", "classify")
    graph.add_edge("classify", END)

    app = graph.compile()
    result = app.invoke({"raw_event": "no_helmet", "status": "pending", "messages": []})

    print(f"  嚴重程度：{result['severity']}")
    print(f"  歷程：{result['messages']}")


# === Demo 2：三種 Node 串接 ===

def demo_three_node_types():
    print("\n=== Demo 2：三種 Node 串接 ===\n")

    if not os.getenv("GOOGLE_API_KEY"):
        print("  跳過（需要 GOOGLE_API_KEY）")
        return

    graph = StateGraph(SafetyState)
    graph.add_node("parse", parse_event)          # 邏輯 Node
    graph.add_node("classify", classify_event)     # 邏輯 Node
    graph.add_node("search_reg", search_regulation) # Tool Node
    graph.add_node("analyze", analyze_with_llm)    # LLM Node

    graph.add_edge(START, "parse")
    graph.add_edge("parse", "classify")
    graph.add_edge("classify", "search_reg")
    graph.add_edge("search_reg", "analyze")
    graph.add_edge("analyze", END)

    app = graph.compile()
    result = app.invoke({"raw_event": "no_helmet", "status": "pending", "messages": []})

    print(f"  法規：{result['regulation']}")
    print(f"  歷程：")
    for msg in result["messages"]:
        print(f"    {msg}")


if __name__ == "__main__":
    demo_logic_nodes()
    demo_three_node_types()
