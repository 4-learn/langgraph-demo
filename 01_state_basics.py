"""
Demo：LangGraph Hello World — 計數器

對應講義：LangGraph 簡介

執行方式：
  python 01_state_basics.py

需要：
  pip install langgraph
"""

from langgraph.graph import StateGraph, START, END
from typing import TypedDict


# State
class CounterState(TypedDict):
    count: int


# Node
def increment(state: CounterState) -> CounterState:
    return {"count": state["count"] + 1}


def double(state: CounterState) -> CounterState:
    return {"count": state["count"] * 2}


# Demo 1: 單節點
def demo_single():
    print("=== Demo 1：單節點 ===")

    graph = StateGraph(CounterState)
    graph.add_node("increment", increment)
    graph.add_edge(START, "increment")
    graph.add_edge("increment", END)

    app = graph.compile()
    result = app.invoke({"count": 0})
    print(f"  0 → +1 = {result['count']}")


# Demo 2: 兩節點串接
def demo_two_nodes():
    print("\n=== Demo 2：兩節點串接 ===")

    graph = StateGraph(CounterState)
    graph.add_node("increment", increment)
    graph.add_node("double", double)
    graph.add_edge(START, "increment")
    graph.add_edge("increment", "double")
    graph.add_edge("double", END)

    app = graph.compile()
    result = app.invoke({"count": 3})
    print(f"  3 → +1 = 4 → *2 = {result['count']}")


if __name__ == "__main__":
    demo_single()
    demo_two_nodes()
