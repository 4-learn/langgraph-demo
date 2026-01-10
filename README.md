# LangGraph Demo

狀態與流程層（State & Workflow）的 Demo 程式碼 - Graph-based Orchestration。

## 安裝

```bash
pip install -r requirements.txt
```

## 設定

```bash
export OPENAI_API_KEY="your-api-key"
```

## 檔案說明

| 檔案 | 說明 |
|------|------|
| `01_state_basics.py` | State 狀態管理基礎 |
| `02_graph_structure.py` | Graph 結構：Node、Edge |
| `03_conditional_edges.py` | 條件分支與路徑選擇 |
| `04_loops_and_cycles.py` | 回路與循環控制 |
| `05_safety_workflow.py` | 工安監控工作流程範例 |

## 執行

```bash
# State 基礎
python 01_state_basics.py

# Graph 結構
python 02_graph_structure.py

# 工安工作流程
python 05_safety_workflow.py
```

## 核心概念

```
Graph = Nodes + Edges + State

State: 在節點間傳遞的資料
Node: 執行特定操作的函數
Edge: 節點之間的連接（可以是條件式的）
```

## LangGraph vs LangChain

| 面向 | LangChain | LangGraph |
|------|-----------|-----------|
| 流程 | 線性 Chain | 圖狀 Graph |
| 控制 | 固定順序 | 條件分支、循環 |
| 狀態 | 隱式傳遞 | 顯式管理 |
| 適用 | 簡單流程 | 複雜工作流程 |
