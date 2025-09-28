# nqu_agent_graphrag

# GraphRAG 使用流程紀錄

## 環境需求
- **LLM 模型**: [Ollama](https://ollama.com/)  
  - 指定模型: `Qwen3-30B-A3B-Instruct`
- **Embedding 模型**: `bge-m3`
- **GraphRAG**: 已安裝於本機 (>= v2.5.0)

---

## 初始化專案

在欲建立專案的目錄下執行：

```bash
graphrag init --root .
```

這會建立必要的結構（`settings.yaml`, `data/`, `output/` 等）。

---

## 建立索引

使用 `--verbose` 觀察過程：

```bash
graphrag index --root . --verbose
```

會生成以下重要檔案：
- `text_units.parquet` → 切割後的文本片段
- `entities.parquet` → 辨識出來的實體
- `relationships.parquet` → 各實體之間的關聯
- `communities.parquet` → 社群聚類結果
- `community_reports.parquet` → 社群說明文件
- `context.json` → 全域查詢時的輔助上下文

---

## 全域查詢

執行全域查詢（即 knowledge graph 模式）：

```bash
graphrag query --root . --method global --query "你的問題"
```

> ⚠️ 注意：若查詢空字串 `""`，僅會測試流程是否正常執行。

---

## 模型設定

`settings.yaml` 中需確認以下部分：

```yaml
llm:
  provider: ollama
  model: Qwen3-30B-A3B-Instruct

embedding:
  provider: ollama
  model: bge-m3
```

---

## 使用注意
- 避免使用 `deepseek-r1` 系列模型，因為在查詢時會將「思考過程 (think)」內容輸出，造成結果冗長。
- 建議優先使用 `Qwen3-30B-A3B-Instruct` 或其他乾淨輸出的 instruct 模型。

---

## 常見檔案清單
執行後目錄中會出現：
- `documents.parquet`
- `text_units.parquet`
- `entities.parquet`
- `relationships.parquet`
- `communities.parquet`
- `community_reports.parquet`
- `context.json`
- `stats.json`

---
