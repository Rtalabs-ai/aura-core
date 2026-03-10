<p align="center">
  <img src="https://raw.githubusercontent.com/Rtalabs-ai/aura-core/main/logo.png" alt="Aura" width="100">
</p>

# 🔥 Aura for OpenAI Codex

**Give your Codex agent a persistent knowledge base and 3-tier memory compiled from any documents.**

<p align="center">
  <a href="https://pypi.org/project/auralith-aura/"><img src="https://badge.fury.io/py/auralith-aura.svg" alt="PyPI"></a>
  <a href="https://github.com/Rtalabs-ai/aura-core#-license"><img src="https://img.shields.io/badge/License-Apache_2.0_+_Proprietary-blue.svg" alt="License"></a>
</p>

## What This Does

This skill gives your Codex agent the ability to:

1. **Compile** any folder of documents (PDFs, DOCX, code, spreadsheets, markdown — 60+ formats) into a `.aura` knowledge base
2. **Query** that knowledge base instantly with natural language
3. **Remember** facts and context across sessions with the 3-tier Memory OS (pad, episodic, fact)

> **Memory OS v2.1** (`auralith-aura>=0.2.2`): Enhanced with temporal decay scoring, noise filtering, deduplication, bloom filters, SimHash fuzzy matching, and tiered priority scoring — zero RAM overhead.

All processing happens **locally on your machine**. No data leaves your device.

## Setup

### 1. Install Aura Core

```bash
pip install auralith-aura
```

### 2. Add the Skill

Copy the `SKILL.md` and `scripts/` directory into your Codex skills folder:

```bash
# User-wide (available in all projects)
mkdir -p ~/.codex/skills/aura
cp SKILL.md scripts/ ~/.codex/skills/aura/

# Or project-specific (shared via version control)
mkdir -p .codex/skills/aura
cp SKILL.md scripts/ .codex/skills/aura/
```

## Usage

### Compile a Knowledge Base

```
You: Compile all documentation in ./docs into a knowledge base
Codex: Running: aura compile ./docs --output knowledge.aura
       ✅ Knowledge base compiled — documents indexed
```

### Query Documents

```
You: Search the knowledge base for how the payment system works
Codex: Found relevant documents:
       📄 payment_flow.md
       📄 stripe_integration.py
       📄 api_reference.md
```

### Use Agent Memory

```
You: Remember that our production database is on us-east-1
Codex: ✅ Written to fact tier

--- next session ---

You: Where is our production database?
Codex: Based on stored memory: Your production database is on us-east-1
```

## How It Works

```python
# The skill uses Aura's Python API
from aura.rag import AuraRAGLoader

loader = AuraRAGLoader("knowledge.aura")

# Get text from any document
text = loader.get_text_by_id("payment_flow")

# Search across all documents
for doc_id, text, meta in loader.iterate_texts():
    if "payment" in text.lower():
        print(f"Found: {meta['source']}")

# Framework wrappers
langchain_docs = loader.to_langchain_documents()
llama_docs = loader.to_llama_index_documents()
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
