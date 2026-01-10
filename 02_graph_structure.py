"""
Graph 結構：Node、Edge

學習目標：
1. 建立 StateGraph
2. 定義 Node
3. 連接 Edge
4. 編譯和執行 Graph
"""

from typing import TypedDict, Annotated
from operator import add


def demo_graph_concept():
    """Graph 概念"""
    print("=== Graph 概念 ===\n")

    print("""
# Graph = Nodes + Edges + State

    ┌─────────┐
    │  START  │
    └────┬────┘
         │
    ┌────▼────┐
    │  Node A │  ← 執行某個操作
    └────┬────┘
         │
    ┌────▼────┐
    │  Node B │  ← 執行另一個操作
    └────┬────┘
         │
    ┌────▼────┐
    │   END   │
    └─────────┘

State 在每個 Node 之間傳遞
每個 Node 可以讀取和更新 State
""")


def demo_basic_graph():
    """基本 Graph 建立"""
    print("\n=== 基本 Graph 建立 ===\n")

    print("""
from langgraph.graph import StateGraph, START, END

# 1. 定義 State
class MyState(TypedDict):
    input: str
    result: str

# 2. 建立 Graph Builder
graph = StateGraph(MyState)

# 3. 定義 Node 函數
def process_node(state: MyState) -> dict:
    '''處理節點'''
    return {"result": f"處理了: {state['input']}"}

# 4. 加入 Node
graph.add_node("process", process_node)

# 5. 加入 Edge
graph.add_edge(START, "process")  # START → process
graph.add_edge("process", END)    # process → END

# 6. 編譯
compiled = graph.compile()

# 7. 執行
result = compiled.invoke({"input": "測試"})
print(result)  # {"input": "測試", "result": "處理了: 測試"}
""")

    # 實際執行（如果有安裝 langgraph）
    try:
        from langgraph.graph import StateGraph, START, END

        class MyState(TypedDict):
            input: str
            result: str

        def process_node(state: MyState) -> dict:
            return {"result": f"處理了: {state['input']}"}

        graph = StateGraph(MyState)
        graph.add_node("process", process_node)
        graph.add_edge(START, "process")
        graph.add_edge("process", END)

        compiled = graph.compile()
        result = compiled.invoke({"input": "測試資料"})

        print("執行結果:")
        print(f"  input: {result['input']}")
        print(f"  result: {result['result']}")

    except ImportError:
        print("(需安裝 langgraph 才能執行)")


def demo_multiple_nodes():
    """多節點 Graph"""
    print("\n=== 多節點 Graph ===\n")

    print("""
# 多個節點順序執行

class PipelineState(TypedDict):
    data: str
    steps: Annotated[list, add]

def step1(state):
    return {
        "data": state["data"] + "_step1",
        "steps": ["step1"]
    }

def step2(state):
    return {
        "data": state["data"] + "_step2",
        "steps": ["step2"]
    }

def step3(state):
    return {
        "data": state["data"] + "_step3",
        "steps": ["step3"]
    }

graph = StateGraph(PipelineState)
graph.add_node("step1", step1)
graph.add_node("step2", step2)
graph.add_node("step3", step3)

graph.add_edge(START, "step1")
graph.add_edge("step1", "step2")
graph.add_edge("step2", "step3")
graph.add_edge("step3", END)

# 執行：START → step1 → step2 → step3 → END
result = graph.compile().invoke({"data": "input", "steps": []})
# result = {"data": "input_step1_step2_step3", "steps": ["step1", "step2", "step3"]}
""")

    try:
        from langgraph.graph import StateGraph, START, END

        class PipelineState(TypedDict):
            data: str
            steps: Annotated[list, add]

        def step1(state):
            return {"data": state["data"] + "_A", "steps": ["A"]}

        def step2(state):
            return {"data": state["data"] + "_B", "steps": ["B"]}

        def step3(state):
            return {"data": state["data"] + "_C", "steps": ["C"]}

        graph = StateGraph(PipelineState)
        graph.add_node("step1", step1)
        graph.add_node("step2", step2)
        graph.add_node("step3", step3)

        graph.add_edge(START, "step1")
        graph.add_edge("step1", "step2")
        graph.add_edge("step2", "step3")
        graph.add_edge("step3", END)

        result = graph.compile().invoke({"data": "start", "steps": []})
        print(f"執行結果: {result}")

    except ImportError:
        print("(需安裝 langgraph 才能執行)")


def demo_node_types():
    """Node 類型"""
    print("\n=== Node 類型 ===\n")

    print("""
# Node 可以是：

# 1. 普通函數
def my_node(state):
    return {"result": "processed"}

# 2. LLM Chain
from langchain_openai import ChatOpenAI
llm = ChatOpenAI()
graph.add_node("llm", llm)  # 直接加入 LLM

# 3. Tool
from langchain_core.tools import tool

@tool
def search_tool(query: str) -> str:
    '''搜尋工具'''
    return f"搜尋結果: {query}"

# 4. 子圖 (SubGraph)
sub_graph = StateGraph(SubState)
# ... 定義子圖 ...
graph.add_node("sub_process", sub_graph.compile())

# 5. 類別方法
class Processor:
    def __init__(self, config):
        self.config = config

    def process(self, state):
        return {"result": f"config={self.config}"}

processor = Processor("my_config")
graph.add_node("process", processor.process)
""")


def demo_entry_point():
    """設定入口點"""
    print("\n=== 設定入口點 ===\n")

    print("""
# 指定 Graph 的起始節點

# 方法 1: add_edge from START
graph.add_edge(START, "first_node")

# 方法 2: set_entry_point（舊 API，建議用 add_edge）
graph.set_entry_point("first_node")

# 動態入口：根據輸入決定起始節點
def route_start(state):
    if state.get("urgent"):
        return "urgent_handler"
    return "normal_handler"

graph.add_conditional_edges(START, route_start)
""")


def demo_compile_options():
    """編譯選項"""
    print("\n=== 編譯選項 ===\n")

    print("""
# 編譯時的選項

# 基本編譯
compiled = graph.compile()

# 加入 Checkpointer（狀態持久化）
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()
compiled = graph.compile(checkpointer=checkpointer)

# 執行時指定 thread_id（用於持久化）
result = compiled.invoke(
    {"input": "..."},
    config={"configurable": {"thread_id": "user_001"}}
)

# 加入中斷點（人工審核）
compiled = graph.compile(
    checkpointer=checkpointer,
    interrupt_before=["sensitive_node"],  # 執行前中斷
    interrupt_after=["review_node"],      # 執行後中斷
)
""")


def demo_invoke_options():
    """執行選項"""
    print("\n=== 執行選項 ===\n")

    print("""
# 執行 Graph 的方式

# 1. 基本執行
result = compiled.invoke({"input": "..."})

# 2. 串流執行
for event in compiled.stream({"input": "..."}):
    print(event)  # 每個節點執行後輸出

# 3. 串流模式選擇
for event in compiled.stream({"input": "..."}, stream_mode="values"):
    print(event)  # 輸出完整 state

for event in compiled.stream({"input": "..."}, stream_mode="updates"):
    print(event)  # 只輸出 state 變更

# 4. 帶配置執行
result = compiled.invoke(
    {"input": "..."},
    config={
        "configurable": {"thread_id": "123"},
        "recursion_limit": 50,  # 最大遞迴次數
    }
)

# 5. Debug 模式
result = compiled.invoke({"input": "..."}, debug=True)
""")


# === 主程式 ===
if __name__ == "__main__":
    print("=" * 50)
    print("Graph 結構：Node、Edge")
    print("=" * 50)
    print()

    demo_graph_concept()
    demo_basic_graph()
    demo_multiple_nodes()
    demo_node_types()
    demo_entry_point()
    demo_compile_options()
    demo_invoke_options()

    print("\n完成！")
