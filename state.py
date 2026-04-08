import operator
from typing import Annotated, TypedDict
from langgraph.graph import add_messages


class SupervisorState(TypedDict):
    event: dict
    severity: str
    regulation_result: str
    report_result: str
    notification_result: str
    next_agent: str
    completed_agents: Annotated[list[str], operator.add]  # 累加，不是覆蓋
    messages: Annotated[list, add_messages]
