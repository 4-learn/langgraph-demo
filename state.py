from typing import Annotated, TypedDict
from langgraph.graph import add_messages


class SupervisorState(TypedDict):
    event: dict
    severity: str
    regulation_result: str
    report_result: str
    notification_result: str
    next_agent: str
    completed_agents: list[str]
    messages: Annotated[list, add_messages]
