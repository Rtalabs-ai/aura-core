<p align="center">
  <img src="logo.png" alt="Rta Labs Logo" width="120">
  <h1 align="center">Aura: The Universal Context Compiler</h1>
  <p align="center">
    <strong>Compile any document into AI-ready knowledge bases with built-in agent memory.</strong>
  </p>
</p>

<p align="center">
  <a href="https://pypi.org/project/auralith-aura/"><img src="https://badge.fury.io/py/auralith-aura.svg" alt="PyPI version"></a>
  <a href="https://github.com/Rtalabs-ai/aura-core#-license"><img src="https://img.shields.io/badge/License-Apache_2.0_+_Proprietary-blue.svg" alt="License"></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="Python 3.8+"></a>
  <a href="https://github.com/Rtalabs-ai/aura-core"><img src="https://img.shields.io/badge/platform-macOS%20%7C%20Windows%20%7C%20Linux-lightgrey" alt="Platform"></a>
</p>

<p align="center">
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-agent-memory">Agent Memory</a> •
  <a href="#-agent-integrations">Integrations</a> •
  <a href="#-rag-support">RAG Support</a> •
  <a href="https://aura.rtalabs.org">Website</a>
</p>

---

## Context is the new Compute.

Aura compiles messy, real-world files (PDFs, DOCX, HTML, code, spreadsheets — **60+ formats**) into a single optimized binary (`.aura`) ready for **RAG retrieval** and **AI agent memory**.

One command. No JSONL scripting. No parsing pipelines.

```bash
pip install auralith-aura
aura compile ./my_data/ --output knowledge.aura
```

---

## ⚡ Quick Start

### 1. Install

```bash
pip install auralith-aura

# For full document support (PDFs, DOCX, etc.)
pip install 'auralith-aura[all]'
```

### 2. Compile

```bash
# Basic compilation
aura compile ./company_data/ --output knowledge.aura

# With PII masking (emails, phones, SSNs automatically redacted)
aura compile ./data/ --output knowledge.aura --pii-mask

# Filter low-quality content
aura compile ./data/ --output knowledge.aura --min-quality 0.3
```

### 3. Use

**For RAG (Knowledge Retrieval):**
```python
from aura.rag import AuraRAGLoader

loader = AuraRAGLoader("knowledge.aura")
text = loader.get_text_by_id("doc_001")

# Framework wrappers
langchain_docs = loader.to_langchain_documents()
llama_docs = loader.to_llama_index_documents()
```

**For Agent Memory:**
```python
from aura.memory import AuraMemoryOS

memory = AuraMemoryOS()

# Write to memory tiers
memory.write("fact", "User prefers dark mode", source="agent")
memory.write("episodic", "Discussed deployment strategy")
memory.write("pad", "TODO: check auth module")

# Search memory
results = memory.query("user preferences")

# End session (flushes to durable shards)
memory.end_session()
```

---

## 🧠 Agent Memory

Aura includes a **3-Tier Memory OS** — a persistent memory architecture for AI agents:

| Tier | Purpose | Lifecycle |
|------|---------|-----------|
| `/pad` | Working notes, scratch space | Transient |
| `/episodic` | Session transcripts, conversation history | Auto-archived |
| `/fact` | Verified facts, user preferences | Persistent |

The Memory OS is **included free** when you install from PyPI (`pip install auralith-aura`).

```bash
# CLI memory management
aura memory list       # View all memory shards
aura memory usage      # Storage usage by tier
aura memory prune --before 2026-01-01  # Clean up old memories
```

### v2.1 Performance Enhancements

Memory OS v2.1 (`auralith-aura>=0.2.2`) adds six performance enhancements designed for **zero RAM overhead** — no embedding models, no vector databases, no background services:

| Enhancement | What It Does |
|-------------|-------------|
| **Temporal Decay** | Recent memories rank higher (14-day half-life recency boost) |
| **Noise Filtering** | Blocks meta-questions and agent denials from storage and search |
| **Entry Dedup** | SHA-256 + SimHash near-duplicate detection prevents redundant writes |
| **Bloom Filters** | ~1KB per shard — skips irrelevant shards entirely during query |
| **SimHash** | 64-bit locality-sensitive hashing for fuzzy text matching without embeddings |
| **Tiered Scoring** | Facts rank above episodic, episodic above pad in search results |

Upgrade: `pip install --upgrade auralith-aura`

### Data Provenance & Trust

Every memory entry stores explicit metadata — you always know what's in memory and where it came from:

| Field | What It Tells You |
|-------|------------------|
| `source` | Who wrote it — `agent`, `user`, or `system` |
| `namespace` | Which tier — `pad`, `episodic`, or `fact` |
| `timestamp` | Exact ISO 8601 time of the write |
| `session_id` | Which session created it |
| `entry_id` | Unique content hash for traceability |

**Nothing is inferred or synthesized.** Memory contains only what was explicitly written via `write()`. No hidden embeddings, no derived data, no background processing.

**Full user control over memory:**
```bash
memory.show_usage()                              # Inspect what's stored per tier
memory.query("topic")                            # See exactly what's in memory
memory.prune_shards(before_date="2026-01-01")    # Prune by date
memory.prune_shards(shard_ids=["specific_id"])   # Delete specific shards
# Or delete ~/.aura/memory/ to wipe everything
```

---

## 🤖 Agent Integrations

Aura works natively with the major AI agent platforms:

| Platform | Repo | Use Case |
|----------|------|----------|
| **OpenClaw** | [`aura-openclaw`](https://github.com/Rtalabs-ai/aura-openclaw) | Persistent RAG + memory for always-on agents |
| **Claude Code** | [`aura-claude-code`](https://github.com/Rtalabs-ai/aura-claude-code) | Context-aware coding with `/aura` commands |
| **OpenAI Codex** | [`aura-codex`](https://github.com/Rtalabs-ai/aura-codex) | Knowledge-backed Codex agents |
| **Gemini CLI** | [`aura-gemini-cli`](https://github.com/Rtalabs-ai/aura-gemini-cli) | Gemini CLI extension for RAG |

### How It Works (Agent RAG Flow)

```
You: "Learn everything in my /docs/ folder"
  → Agent runs: aura compile ./docs/ --output knowledge.aura
  → Agent loads: AuraRAGLoader("knowledge.aura")
  → You: "What does the auth module do?"
  → Agent queries the .aura file and responds with cited answers
```

---

## 🌟 Key Features

| Feature | Description |
|---------|-------------|
| **Universal Ingestion** | Parses 60+ formats: PDF, DOCX, HTML, MD, CSV, code, and more |
| **Agent Memory OS** | 3-tier memory (pad/episodic/fact) with instant writes |
| **PII Masking** | Automatically redacts emails, phones, SSNs before compilation |
| **Instant RAG** | Query any document by keyword or ID. LangChain + LlamaIndex wrappers |
| **Quality Filtering** | Skip low-quality content with configurable thresholds |
| **Cross-Platform** | macOS, Windows, and Linux |
| **Secure by Design** | No pickle. No arbitrary code execution. Safe to share. |

---

## 📁 Supported File Formats

<details>
<summary><b>Documents</b> - PDF, DOCX, HTML, and more</summary>

- `.pdf`, `.docx`, `.doc`, `.rtf`, `.odt`, `.epub`, `.txt`, `.pages`, `.wpd`
- `.html`, `.htm`, `.xml`
- `.eml`, `.msg` (emails)
- `.pptx`, `.ppt` (presentations)

</details>

<details>
<summary><b>Data</b> - Spreadsheets and structured data</summary>

- `.csv`, `.tsv`
- `.xlsx`, `.xls`
- `.parquet`
- `.json`, `.jsonl`
- `.yaml`, `.yml`, `.toml`

</details>

<details>
<summary><b>Code</b> - All major programming languages</summary>

- **Python**: `.py`, `.pyi`, `.ipynb`
- **Web**: `.js`, `.ts`, `.jsx`, `.tsx`, `.css`
- **Systems**: `.c`, `.cpp`, `.h`, `.hpp`, `.rs`, `.go`, `.java`, `.kt`, `.swift`
- **Scripts**: `.sh`, `.bash`, `.zsh`, `.ps1`, `.bat`
- **Backend**: `.sql`, `.php`, `.rb`, `.cs`, `.scala`
- **Config**: `.ini`, `.cfg`, `.conf`, `.env`, `.dockerfile`

</details>

<details>
<summary><b>Markup</b> - Documentation formats</summary>

- `.md` (Markdown)
- `.rst` (reStructuredText)
- `.tex`, `.latex`

</details>

---

## 🔧 CLI Reference

```bash
aura compile <input_directory> --output <file.aura> [options]

Options:
  --pii-mask           Mask PII (emails, phones, SSNs)
  --min-quality SCORE  Filter low-quality content (0.0-1.0)
  --domain DOMAIN      Tag with domain context
  --no-recursive       Don't search subdirectories
  --verbose, -v        Verbose output
```

### Memory Management

```bash
aura memory list                        # List all memory shards
aura memory usage                       # Show storage by tier
aura memory prune --before 2026-01-01   # Remove old shards
aura memory prune --id <shard_id>       # Remove specific shard
```

### Inspect an Archive

```bash
aura info knowledge.aura

📦 Aura Archive: knowledge.aura
   Datapoints: 1,234
   
   Sample datapoint:
     Tensors: ['raw_text']
     Source:  legal/contract_001.pdf
```

---

## 🔌 RAG Support

```python
from aura.rag import AuraRAGLoader

loader = AuraRAGLoader("knowledge.aura")

# Text retrieval
text = loader.get_text_by_id("doc_001")

# Filter documents
pdf_docs = loader.filter_by_extension(".pdf")
legal_docs = loader.filter_by_source("legal/")

# Framework wrappers
langchain_docs = loader.to_langchain_documents()  # LangChain
llama_docs = loader.to_llama_index_documents()     # LlamaIndex
dict_list = loader.to_dict_list()                  # Universal

# Statistics
stats = loader.get_stats()
```

---

## 📐 File Format Specification

The `.aura` format is a secure, indexed binary archive:

```
[Datapoint 1][Datapoint 2]...[Datapoint N][Index][Footer]

Each Datapoint:
  [meta_length: 4 bytes, uint32]
  [tensor_length: 4 bytes, uint32]
  [metadata: msgpack bytes]
  [tensors: safetensors bytes]

Footer:
  [index_offset: 8 bytes, uint64]
  [magic: 4 bytes, 'AURA']
```

**Security**: Uses `safetensors` (not pickle) — safe to load untrusted files.

---

## 💻 Runs Locally

Aura compiles entirely on your local machine — no cloud uploads, no external APIs, no telemetry.

- **Runs on your local hardware** — any modern laptop or desktop, your setup, your choice
- **Fully offline** — zero internet required after install
- **Cross-platform** — macOS, Windows, Linux
- **Python 3.8+**

Your documents never leave your hardware.

---

## 🚀 Scale Up with OMNI

Aura handles local compilation. For enterprise-scale training pipelines, model fine-tuning, and production-grade agent infrastructure — there's **OMNI**.

- Cloud-scale data compilation & training pipelines
- Supervised model fine-tuning with emphasis weighting
- Production agent memory infrastructure
- Team collaboration & enterprise compliance

**[Explore OMNI →](https://omni.rtalabs.org)**

---

## 📜 License

- **Compiler, RAG, Loader, Binary Format**: [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0)
- **Memory OS**: Proprietary — free to use, included in PyPI package. See [LICENSE-MEMORY](https://github.com/Rtalabs-ai/aura-core/blob/main/LICENSE-MEMORY).

---

## 🔗 Links

- **Website**: [aura.rtalabs.org](https://aura.rtalabs.org)
- **PyPI**: [pypi.org/project/auralith-aura](https://pypi.org/project/auralith-aura)
- **GitHub**: [github.com/Rtalabs-ai/aura-core](https://github.com/Rtalabs-ai/aura-core)
- **OpenClaw Skill**: [github.com/Rtalabs-ai/aura-openclaw](https://github.com/Rtalabs-ai/aura-openclaw)

---

<p align="center">
Made with ❤️ by <a href="https://rtalabs.org">Rta Labs</a>
</p>
