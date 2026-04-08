from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini")


def regulation_agent(state: dict) -> dict:
    """法規 Agent：查詢事件相關法規"""
    event = state["event"]
    category = event.get("category", "未分類")

    # 這裡可以接 MCP Server（上一節學的）
    # 現在先用 LLM 生成
    response = llm.invoke(
        f"你是工安法規專家。針對「{category}」類型的違規事件，"
        f"列出最相關的法規條文和罰則。簡潔回答。"
    )

    return {
        "regulation_result": response.content,
        "completed_agents": ["regulation"],
        "messages": [f"📋 法規 Agent 完成：已查詢 {category} 相關法規"],
    }


def report_agent(state: dict) -> dict:
    """報告 Agent：根據事件和法規產出正式報告"""
    event = state["event"]
    regulation = state.get("regulation_result", "尚未查詢")

    response = llm.invoke(
        f"你是工安報告撰寫專家。根據以下資訊撰寫正式的工安事件報告：\n"
        f"事件：{event}\n"
        f"相關法規：{regulation}\n"
        f"格式：標題、事件摘要、違規事實、法規依據、改善建議"
    )

    return {
        "report_result": response.content,
        "completed_agents": ["report"],
        "messages": ["📝 報告 Agent 完成：已產出事件報告"],
    }


def notification_agent(state: dict) -> dict:
    """通知 Agent：根據事件嚴重程度發送通知"""
    severity = state["severity"]

    notify_targets = {
        "高": ["工地主任", "安全主管", "勞檢單位"],
        "中": ["工地主任", "安全主管"],
        "低": ["工地主任"],
    }

    targets = notify_targets.get(severity, ["工地主任"])
    notifications = [f"  ✉ 已通知 {t}" for t in targets]
    result = f"通知已發送（{severity}風險）：\n" + "\n".join(notifications)

    return {
        "notification_result": result,
        "completed_agents": ["notification"],
        "messages": [f"🔔 通知 Agent 完成：已通知 {len(targets)} 人"],
    }
