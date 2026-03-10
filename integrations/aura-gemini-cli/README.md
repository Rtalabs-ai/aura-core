<p align="center">
  <img src="https://raw.githubusercontent.com/Rtalabs-ai/aura-core/main/logo.png" alt="Aura" width="100">
</p>

# 🔥 Aura for Gemini CLI

**Give your Gemini CLI agent a persistent knowledge base and 3-tier memory compiled from any documents.**

<p align="center">
  <a href="https://pypi.org/project/auralith-aura/"><img src="https://badge.fury.io/py/auralith-aura.svg" alt="PyPI"></a>
  <a href="https://opensource.org/licenses/Apache-2.0"><img src="https://img.shields.io/badge/License-Apache_2.0-blue.svg" alt="License: Apache 2.0"></a>
</p>

## What This Does

This extension gives your Gemini CLI agent the ability to:

1. **Compile** any folder of documents (PDFs, DOCX, code, spreadsheets, markdown — 60+ formats) into a `.aura` knowledge base
2. **Query** that knowledge base instantly with natural language
3. **Remember** context across sessions with the 3-tier Memory OS (pad, episodic, fact)

> **Memory OS v2.1** (`auralith-aura>=0.2.2`): Enhanced with temporal decay scoring, noise filtering, deduplication, bloom filters, SimHash fuzzy matching, and tiered priority scoring — zero RAM overhead.

All processing happens **locally on your machine**. No data leaves your device.

## Install

### 1. Install Aura Core

```bash
pip install auralith-aura
```

### 2. Install the Extension

```bash
gemini extensions install https://github.com/Rtalabs-ai/aura-gemini-cli
```

That's it. The extension configures Aura's MCP server automatically — all tools are available immediately.

## Available Tools

Once installed, your Gemini CLI agent has access to these tools:

| Tool | Description |
|------|-------------|
| `aura_compile` | Compile a directory into a `.aura` knowledge base |
| `aura_query` | Search a knowledge base for relevant documents |
| `aura_memory_write` | Write to persistent memory (pad / episodic / fact) |
| `aura_memory_query` | Search persistent memory |
| `aura_memory_list` | List all stored memory entries |
| `aura_info` | Inspect an `.aura` archive (doc count, file types, size) |

## Custom Commands

The extension also provides slash commands:

- `/aura-compile <directory>` — Compile documents into a knowledge base
- `/aura-query <aura_file> <query>` — Search a knowledge base
- `/aura-memory <action> [args]` — Manage persistent agent memory

## Usage

### Compile a Knowledge Base

```
You: Compile all the docs in ./docs into a knowledge base
Gemini: [uses aura_compile] ✅ Compiled ./docs → knowledge.aura (47 documents indexed)
```

### Query Documents

```
You: Search the knowledge base for how authentication works
Gemini: [uses aura_query] Found relevant documents:
        📄 auth_module.py (relevance: 4)
        📄 architecture.md (relevance: 3)
```

### Persistent Memory

```
You: Remember that our staging API is at api-staging.example.com
Gemini: [uses aura_memory_write] ✅ Written to fact tier

--- next session ---

You: What's our staging API URL?
Gemini: [uses aura_memory_query] Based on stored memory: api-staging.example.com
```

## How It Works

The extension packages Aura Core as an [MCP server](https://modelcontextprotocol.io/) that Gemini CLI discovers and calls automatically. Under the hood:

```python
from aura.rag import AuraRAGLoader

loader = AuraRAGLoader("knowledge.aura")
text = loader.get_text_by_id("auth_module")
docs = loader.to_langchain_documents()
```

## Data Provenance & Trust

Every memory entry stores `source` (agent/user/system), `namespace`, `timestamp`, `session_id`, and a unique `entry_id`. Nothing is inferred or synthesized — memory contains only what was explicitly written. No hidden embeddings, no derived data.

```python
memory.show_usage()                              # Inspect what's stored per tier
memory.prune_shards(before_date="2026-01-01")    # Prune by date
# Or delete ~/.aura/memory/ to wipe everything
```

## Runs Locally

- **Runs on your local hardware** — any modern laptop or desktop, your setup, your choice
- **Fully offline** — zero internet required after install
- **Cross-platform** — macOS, Windows, Linux, Python 3.8+

Your documents never leave your hardware.

## Scale Up with OMNI

Need enterprise-scale training pipelines, model fine-tuning, or production agent infrastructure? Check out [**OMNI**](https://omni.rtalabs.org).

## Links

- [Aura Core](https://github.com/Rtalabs-ai/aura-core) — The compiler
- [Website](https://aura.rtalabs.org) — Documentation
- [OMNI Platform](https://omni.rtalabs.org) — Enterprise scale
- [PyPI](https://pypi.org/project/auralith-aura/) — Install

---

Made by [Rta Labs](https://rtalabs.org)
