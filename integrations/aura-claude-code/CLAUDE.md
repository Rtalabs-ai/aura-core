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

Aura provides **Memory OS v2.1** — a 3-tier memory system that persists across sessions:

| Tier | What It Stores | Lifecycle |
|------|---------------|-----------|
| `/pad` | Working notes, scratch space | Transient — cleared between sessions |
| `/episodic` | Session transcripts, decisions | Auto-archived — retained for reference |
| `/fact` | Verified facts, user preferences | Persistent — survives indefinitely |

**v2.1 Features**: Entry deduplication (SimHash), temporal decay scoring, bloom filter shard skipping, append-only (old entries never overwritten), tiered priority (facts > episodic > pad).

Memory operates **both autonomously and manually**:
- **Autonomous**: Agent auto-writes facts during compile/query sessions
- **Manual**: Explicitly write with the commands below

```python
from aura.memory import AuraMemoryOS

memory = AuraMemoryOS()

# Write to any tier
memory.write("fact", "User prefers dark mode")
memory.write("pad", "Check auth module next")
memory.write("episodic", "Reviewed the API routes today")

# Query memory by keyword
results = memory.query("user preferences")

# List all entries
entries = memory.list_entries()

# Show storage usage
memory.show_usage()
```

## Custom Commands

- `/aura-compile <directory>` — Compile documents into a knowledge base
- `/aura-query <file> <question>` — Search a knowledge base
- `/aura-memory <action> [args]` — Manage persistent agent memory

## Research Knowledge Base (Optional)

For research-focused workflows, install [Aura Research](https://github.com/Rtalabs-ai/aura-research):

```bash
pip install aura-research
research init my-project
research ingest raw/
research build           # compile wiki/ → wiki.aura
research search "topic"
research memory show     # full overview of all 3 memory tiers
```

Aura Research turns raw documents into a structured wiki with persistent memory. As the agent, **you are the LLM** — you read docs, write wiki articles, and run CLI commands directly. No API key needed.

## Key Facts

- All processing is local. No network calls.
- Uses safetensors (not pickle) — safe to load untrusted files.
- Cross-platform: macOS, Windows, Linux.
- Compiler and RAG: Apache-2.0. Memory OS: proprietary, free to use.
- Documentation: https://github.com/Rtalabs-ai/aura-core
