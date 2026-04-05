<p align="center">
  <img src="https://github.com/Rtalabs-ai/aura-core/raw/main/logo.png" alt="Rta Labs Logo" width="100">
</p>

# Aura Core — Claude Code Integration

This project uses [Aura Core](https://github.com/Rtalabs-ai/aura-core) for document compilation, RAG retrieval, and agent memory.

## What is Aura?

Aura compiles any documents (PDFs, DOCX, code, spreadsheets, markdown — 60+ formats) into a single `.aura` knowledge archive that can be queried instantly. It also provides a 3-tier memory system (pad, episodic, fact) for persistent agent context across sessions.

## Available Commands

### `/aura-compile` — Compile documents into a knowledge base

Usage: `/aura-compile <directory> [output_file]`

This compiles all files in the given directory into an `.aura` archive for instant retrieval.

### `/aura-query` — Search a knowledge base

Usage: `/aura-query <aura_file> <question>`

This searches through a compiled `.aura` archive and returns the most relevant passages.

### `/aura-memory` — Manage agent memory

Usage: `/aura-memory <action> [args]`

Actions: `write`, `list`, `usage`, `query`

**Memory tiers:**
- **`/pad`** — Working notes, scratch space (transient)
- **`/episodic`** — Session transcripts, conversation history (auto-archived)
- **`/fact`** — Verified facts, user preferences (persistent)

> **Memory OS v2.1** (`auralith-aura>=0.2.3`): Enhanced with temporal decay scoring, noise filtering, deduplication, bloom filters, SimHash fuzzy matching, and tiered priority scoring — zero RAM overhead.

## Quick Setup

1. Install Aura Core: `pip install auralith-aura`
2. Copy the `.claude/commands/` directory into your project
3. Use `/aura-compile ./docs` to build a knowledge base
4. Use `/aura-query knowledge.aura "your question"` to search

## How It Works

```
You: /aura-compile ./docs
Claude: 🔥 Compiling ./docs → knowledge.aura
        ✅ Knowledge base created — documents indexed

You: /aura-query knowledge.aura "how does authentication work?"
Claude: Based on auth_module.py and architecture.md:
        The authentication system uses JWT tokens...
```

## Data Provenance & Trust

Every memory entry stores `source` (agent/user/system), `namespace`, `timestamp`, `session_id`, and a unique `entry_id`. Nothing is inferred or synthesized — memory contains only what was explicitly written. No hidden embeddings, no derived data.

```python
memory.show_usage()                              # Inspect what's stored per tier
memory.prune_shards(before_date="2026-01-01")    # Prune by date
# Or delete ~/.aura/memory/ to wipe everything
```

## Security & Privacy

- All processing happens **locally**. No data leaves your machine.
- Uses `safetensors` (no pickle) — safe and secure.
- Runs on your local hardware. Fully offline after install.
- Compiler and RAG: Apache-2.0. Memory OS: proprietary, free to use.

## Research Knowledge Base (Optional)

For research-focused workflows, install [Aura Research](https://github.com/Rtalabs-ai/aura-research) to build structured wikis from raw documents:

```bash
pip install aura-research
research init my-project && research ingest raw/
research build && research memory show
```

No API key needed — as the agent, you ARE the LLM. Read docs, write wiki articles, run CLI commands directly.

## Scale Up with OMNI

Need enterprise-scale training pipelines or production agent infrastructure? Check out [**OMNI**](https://omni.rtalabs.org).

## Links

- [Aura Core](https://github.com/Rtalabs-ai/aura-core)
- [Website](https://aura.rtalabs.org)
- [OMNI Platform](https://omni.rtalabs.org)
- [PyPI](https://pypi.org/project/auralith-aura/)

Made by [Rta Labs](https://rtalabs.org)
