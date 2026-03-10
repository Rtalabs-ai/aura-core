# Aura Core Context

This project uses **Aura Core** (`pip install auralith-aura`) for document compilation, RAG retrieval, and agent memory.

## What Aura Does

Aura compiles directories of files (PDFs, DOCX, code, spreadsheets, markdown, and 60+ other formats) into a single `.aura` binary archive. This archive supports:

- **Instant text retrieval** (RAG) — query any document by keyword or ID
- **Agent memory** — 3-tier memory system (pad, episodic, fact)
- **PII masking** — automatically redact sensitive data before compilation

## How to Use Aura in This Project

### Compile Documents
```bash
aura compile ./docs/ --output knowledge.aura

# With PII masking
aura compile ./docs/ --output knowledge.aura --pii-mask
```

### Query with Python
```python
from aura.rag import AuraRAGLoader

loader = AuraRAGLoader("knowledge.aura")
text = loader.get_text_by_id("doc_001")

# Framework wrappers
langchain_docs = loader.to_langchain_documents()
llama_docs = loader.to_llama_index_documents()
```

### Agent Memory
```python
from aura.memory import AuraMemoryOS

memory = AuraMemoryOS()
memory.write("fact", "User prefers dark mode")
memory.write("pad", "Check auth module next")
results = memory.query("user preferences")
```

## Custom Commands

- `/aura-compile <directory>` — Compile documents into a knowledge base
- `/aura-query <file> <question>` — Search a knowledge base

## Key Facts

- All processing is local. No network calls.
- Uses safetensors (not pickle) — safe to load untrusted files.
- Cross-platform: macOS, Windows, Linux.
- Compiler and RAG: Apache-2.0. Memory OS: proprietary, free to use.
- Documentation: https://github.com/Rtalabs-ai/aura-core
