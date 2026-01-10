"""
回路與循環控制

學習目標：
1. 循環的概念
2. Agent 循環模式
3. 重試機制
4. 循環終止條件
"""

from typing import TypedDict, Annotated, Literal
from operator import add


def demo_loop_concept():
    """循環概念"""
    print("=== 循環概念 ===\n")

    print("""
# Graph 可以包含循環（Cycle）

    ┌─────────┐
    │  START  │
    └────┬────┘
         │
    ┌────▼────┐
    │  agent  │◄────┐
    └────┬────┘     │
         │          │
    ┌────▼────┐     │
    │  route  │─────┘ (continue)
    └────┬────┘
         │ (end)
    ┌────▼────┐
    │   END   │
    └─────────┘

典型用途：
- Agent 決定呼叫 Tool，然後繼續
- 重試機制
- 迭代優化
""")


def demo_agent_loop():
    """Agent 循環模式"""
    print("\n=== Agent 循環模式 ===\n")

    print("""
# 經典的 Agent 循環

class AgentState(TypedDict):
    messages: Annotated[list, add]  # 對話歷史
    tool_calls: list                 # 待呼叫的 tools

def agent_node(state):
    '''Agent 決定動作'''
    # LLM 決定是否呼叫 tool
    response = llm_with_tools.invoke(state["messages"])

    if response.tool_calls:
        return {
            "messages": [response],
            "tool_calls": response.tool_calls
        }
    return {
        "messages": [response],
        "tool_calls": []
    }

def tool_node(state):
    '''執行 Tools'''
    results = []
    for call in state["tool_calls"]:
        result = execute_tool(call)
        results.append(ToolMessage(content=result))
    return {"messages": results, "tool_calls": []}

def should_continue(state) -> Literal["continue", "end"]:
    if state["tool_calls"]:
        return "continue"
    return "end"

graph = StateGraph(AgentState)
graph.add_node("agent", agent_node)
graph.add_node("tools", tool_node)

graph.add_edge(START, "agent")
graph.add_conditional_edges(
    "agent",
    should_continue,
    {"continue": "tools", "end": END}
)
graph.add_edge("tools", "agent")  # 回到 agent
""")


def demo_retry_loop():
    """重試循環"""
    print("\n=== 重試循環 ===\n")

    print("""
# 失敗時自動重試

class RetryState(TypedDict):
    input: str
    result: str
    error: str
    retry_count: int
    max_retries: int

def process_node(state):
    try:
        # 可能失敗的操作
        result = risky_operation(state["input"])
        return {"result": result, "error": ""}
    except Exception as e:
        return {"error": str(e)}

def increment_retry(state):
    return {"retry_count": state["retry_count"] + 1}

def should_retry(state) -> Literal["success", "retry", "fail"]:
    if not state["error"]:
        return "success"
    if state["retry_count"] < state["max_retries"]:
        return "retry"
    return "fail"

graph = StateGraph(RetryState)
graph.add_node("process", process_node)
graph.add_node("increment", increment_retry)
graph.add_node("success_handler", success_node)
graph.add_node("fail_handler", fail_node)

graph.add_edge(START, "process")
graph.add_conditional_edges(
    "process",
    should_retry,
    {
        "success": "success_handler",
        "retry": "increment",
        "fail": "fail_handler"
    }
)
graph.add_edge("increment", "process")  # 回到 process
graph.add_edge("success_handler", END)
graph.add_edge("fail_handler", END)
""")

    try:
        from langgraph.graph import StateGraph, START, END
        import random

        class RetryState(TypedDict):
            input: str
            result: str
            error: str
            retry_count: int
            max_retries: int

        def process_node(state):
            # 模擬 50% 機率失敗
            if random.random() < 0.5:
                return {"error": "操作失敗", "result": ""}
            return {"result": "成功！", "error": ""}

        def increment_retry(state):
            print(f"  重試 #{state['retry_count'] + 1}")
            return {"retry_count": state["retry_count"] + 1}

        def success_handler(state):
            return {"result": f"最終成功（嘗試 {state['retry_count'] + 1} 次）"}

        def fail_handler(state):
            return {"result": f"失敗（已重試 {state['retry_count']} 次）"}

        def should_retry(state):
            if not state["error"]:
                return "success"
            if state["retry_count"] < state["max_retries"]:
                return "retry"
            return "fail"

        graph = StateGraph(RetryState)
        graph.add_node("process", process_node)
        graph.add_node("increment", increment_retry)
        graph.add_node("success_handler", success_handler)
        graph.add_node("fail_handler", fail_handler)

        graph.add_edge(START, "process")
        graph.add_conditional_edges(
            "process",
            should_retry,
            {"success": "success_handler", "retry": "increment", "fail": "fail_handler"}
        )
        graph.add_edge("increment", "process")
        graph.add_edge("success_handler", END)
        graph.add_edge("fail_handler", END)

        compiled = graph.compile()

        # 測試
        print("執行重試示範：")
        result = compiled.invoke({
            "input": "test",
            "result": "",
            "error": "",
            "retry_count": 0,
            "max_retries": 3
        })
        print(f"  結果: {result['result']}")

    except ImportError:
        print("(需安裝 langgraph 才能執行)")


def demo_iteration_loop():
    """迭代優化循環"""
    print("\n=== 迭代優化循環 ===\n")

    print("""
# 迭代直到達到目標

class OptimizeState(TypedDict):
    data: str
    score: float
    target_score: float
    iterations: int
    max_iterations: int
    history: Annotated[list, add]

def evaluate_node(state):
    '''評估當前結果'''
    score = calculate_score(state["data"])
    return {"score": score, "history": [score]}

def improve_node(state):
    '''改進'''
    improved = improve_data(state["data"])
    return {
        "data": improved,
        "iterations": state["iterations"] + 1
    }

def should_continue(state) -> Literal["continue", "done"]:
    if state["score"] >= state["target_score"]:
        return "done"
    if state["iterations"] >= state["max_iterations"]:
        return "done"
    return "continue"

graph.add_conditional_edges(
    "evaluate",
    should_continue,
    {"continue": "improve", "done": END}
)
graph.add_edge("improve", "evaluate")  # 回到評估
""")


def demo_recursion_limit():
    """遞迴限制"""
    print("\n=== 遞迴限制 ===\n")

    print("""
# 防止無限循環

# 方法 1: 在 invoke 時設定 recursion_limit
result = compiled.invoke(
    initial_state,
    config={"recursion_limit": 50}
)

# 方法 2: 在 state 中追蹤迭代次數
def check_limit(state) -> Literal["continue", "stop"]:
    if state["iterations"] >= 100:
        return "stop"
    return "continue"

# 方法 3: 使用超時
import asyncio

async def run_with_timeout():
    try:
        result = await asyncio.wait_for(
            compiled.ainvoke(state),
            timeout=30.0
        )
    except asyncio.TimeoutError:
        print("執行超時")
""")


def demo_human_in_loop():
    """人工介入循環"""
    print("\n=== 人工介入循環 ===\n")

    print("""
# 需要人工確認的循環

from langgraph.checkpoint.memory import MemorySaver

class ReviewState(TypedDict):
    proposal: str
    approved: bool
    feedback: str
    iterations: int

def generate_node(state):
    '''生成提案'''
    proposal = generate_proposal(state.get("feedback", ""))
    return {"proposal": proposal}

def check_approval(state) -> Literal["approved", "revise", "reject"]:
    if state["approved"]:
        return "approved"
    if state["iterations"] < 3:
        return "revise"
    return "reject"

# 設定中斷點
checkpointer = MemorySaver()
compiled = graph.compile(
    checkpointer=checkpointer,
    interrupt_before=["check_approval"]  # 在檢查前中斷
)

# 執行到中斷點
thread_config = {"configurable": {"thread_id": "review_001"}}
result = compiled.invoke(initial_state, config=thread_config)

# 人工審核後更新 state
compiled.update_state(
    thread_config,
    {"approved": True, "feedback": "很好"}
)

# 繼續執行
result = compiled.invoke(None, config=thread_config)
""")


def demo_parallel_loops():
    """並行循環"""
    print("\n=== 並行循環 ===\n")

    print("""
# 多個獨立的循環

# 使用 Send 發送到多個並行節點
from langgraph.constants import Send

def fan_out(state):
    '''分發到多個處理器'''
    items = state["items"]
    return [Send("processor", {"item": item}) for item in items]

def processor(state):
    '''處理單個項目（可能包含循環）'''
    # 內部循環處理
    result = process_with_retry(state["item"])
    return {"results": [result]}

graph.add_conditional_edges(
    "start",
    fan_out,
    ["processor"]  # 目標節點
)

# 收集結果
def collect(state):
    return {"final": aggregate(state["results"])}

graph.add_edge("processor", "collect")
""")


# === 主程式 ===
if __name__ == "__main__":
    print("=" * 50)
    print("回路與循環控制")
    print("=" * 50)
    print()

    demo_loop_concept()
    demo_agent_loop()
    demo_retry_loop()
    demo_iteration_loop()
    demo_recursion_limit()
    demo_human_in_loop()
    demo_parallel_loops()

    print("\n完成！")
