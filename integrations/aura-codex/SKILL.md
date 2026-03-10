---
name: aura-context-compiler
description: >
  Compile any documents (PDFs, DOCX, code, spreadsheets, markdown — 60+ formats) into a
  queryable .aura knowledge base with a 3-tier persistent memory system (pad, episodic, fact).
  All processing runs locally on your machine. Zero network calls.
---

# Aura Context Compiler

Give your Codex agent persistent knowledge and memory compiled from any documents.

## Setup

Install Aura Core:

```bash
pip install auralith-aura
```

## Capabilities

### Compile Documents

When the user asks you to compile, index, or learn from their documents, run:

```bash
aura compile <directory> --output knowledge.aura
```

To compile with PII masking (redacts emails, phone numbers, SSNs):

```bash
aura compile <directory> --output knowledge.aura --pii-mask
```

### Query a Knowledge Base

To search a compiled knowledge base, use Python:

```python
from aura.rag import AuraRAGLoader

loader = AuraRAGLoader("knowledge.aura")

# Search across all documents
results = []
query = "<search_query>".lower()
for doc_id, text, meta in loader.iterate_texts():
    if not text:
        continue
    score = sum(1 for word in query.split() if word in text.lower())
    if score > 0:
        results.append((score, doc_id, text, meta))

results.sort(key=lambda x: x[0], reverse=True)
for score, doc_id, text, meta in results[:5]:
    source = meta.get("source", doc_id)
    print(f"{source} (relevance: {score})")
    print(f"  {text[:300]}")

loader.close()
```

### Agent Memory

Aura provides a 3-tier memory system that persists across sessions:

- **pad** — Working notes, scratch space, TODO items (transient)
- **episodic** — Session transcripts, conversation summaries (auto-archived)
- **fact** — Verified facts, user preferences, project constants (persistent)

```python
from aura.memory import AuraMemoryOS

memory = AuraMemoryOS()

# Write to memory
memory.write("fact", "User prefers TypeScript and dark mode")
memory.write("pad", "Check auth module for the JWT issue")

# Query memory
results = memory.query("user preferences")
for entry in results:
    print(f"[{entry['tier']}] {entry['content']}")

# List all entries
entries = memory.list_entries()

# Show usage stats
stats = memory.usage()
```

## Security

- All processing happens locally. Zero network calls.
- Uses safetensors (no pickle) — safe to load untrusted files.
- Cross-platform: macOS, Windows, Linux, Python 3.8+.
- Compiler and RAG: Apache-2.0. Memory OS: proprietary, free to use.

## Links

- [Aura Core](https://github.com/Rtalabs-ai/aura-core)
- [PyPI](https://pypi.org/project/auralith-aura/)
- [OMNI Platform](https://omni.rtalabs.org)

Made by [Rta Labs](https://rtalabs.org)
