# Aura Core Context

This project uses **Aura Core** (`pip install auralith-aura`) for document compilation, RAG retrieval, and agent memory.

## What Aura Does

Aura compiles directories of files (PDFs, DOCX, code, spreadsheets, markdown, and 60+ other formats) into a single `.aura` binary archive. This archive supports:

- **Instant text retrieval** (RAG) — query any document by keyword or ID
- **Agent memory** — 3-tier memory system (pad, episodic, fact)
- **PII masking** — automatically redact sensitive data before compilation

## Available MCP Tools

When this extension is installed, the following tools are available:

| Tool | Description |
|------|-------------|
| `aura_compile` | Compile a directory into a `.aura` knowledge base |
| `aura_query` | Search a knowledge base for relevant document passages |
| `aura_memory_write` | Write to persistent memory (pad / episodic / fact tier) |
| `aura_memory_query` | Search persistent memory for entries matching a query |
| `aura_memory_list` | List all stored memory entries |
| `aura_info` | Inspect an `.aura` archive (doc count, types, size) |

## Custom Commands

- `/aura-compile <directory>` — Compile documents into a knowledge base
- `/aura-query <file> <question>` — Search a knowledge base
- `/aura-memory <action> [args]` — Manage persistent agent memory

## Memory OS v2.1

Three-tier persistent memory that survives sessions, compaction, and restarts:

| Tier | What It Stores | Lifecycle |
|------|---------------|-----------|
| `/pad` | Working notes, scratch space | Transient — cleared between sessions |
| `/episodic` | Session transcripts, decisions | Auto-archived — retained for reference |
| `/fact` | Verified facts, user preferences | Persistent — survives indefinitely |

**v2.1 Features**: Entry deduplication (SimHash fuzzy matching), temporal decay scoring, bloom filter shard skipping, append-only storage (old entries never overwritten), tiered priority (facts > episodic > pad).

Memory operates **both autonomously and manually**:
- **Autonomous**: Agent auto-writes facts during compile/query sessions
- **Manual**: Explicitly write with MCP tools or CLI commands

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
- Docs: https://github.com/Rtalabs-ai/aura-core
