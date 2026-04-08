"""LangSmith Hello World：最小驗證，確認 trace 有送到 dashboard"""
from dotenv import load_dotenv
load_dotenv()

from langgraph.graph import StateGraph, START, END
from typing import TypedDict


class HelloState(TypedDict):
    message: str


def say_hello(state: HelloState) -> dict:
    return {"message": "Hello from LangSmith!"}


graph = StateGraph(HelloState)
graph.add_node("say_hello", say_hello)
graph.add_edge(START, "say_hello")
graph.add_edge("say_hello", END)

app = graph.compile()

if __name__ == "__main__":
    result = app.invoke({"message": ""})
    print(result["message"])
    print("\n👉 打開 https://smith.langchain.com → 你的 project，應該看到一條 trace")
