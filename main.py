from supervisor import app

result = app.invoke({
    "event": {
        "id": "EVT-2026-0042",
        "type": "高處墜落",
        "category": "高處墜落",
        "location": "B 棟 12 樓外牆鷹架",
        "description": "工人未繫安全帶於鷹架上作業",
        "time": "2026-04-08 14:30",
    },
    "severity": "高",
    "completed_agents": [],
    "messages": [],
})

print("=== 執行紀錄 ===")
for msg in result["messages"]:
    print(msg)

print("\n=== 法規查詢結果 ===")
print(result["regulation_result"])

print("\n=== 事件報告 ===")
print(result["report_result"])

print("\n=== 通知結果 ===")
print(result["notification_result"])
