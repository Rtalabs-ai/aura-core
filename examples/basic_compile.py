#!/usr/bin/env python3
"""
Aura Core - Basic Example

Demonstrates compiling a directory and querying the resulting knowledge base.
"""
from pathlib import Path

# ─────────────────────────────────────────────
# Step 1: Compile documents into .aura format
# ─────────────────────────────────────────────
from aura.compiler import compile_directory

input_dir = "./my_data"       # Your documents folder
output_file = "knowledge.aura"

# Basic compilation
compile_directory(input_dir, output_file)

# Compilation with PII masking
# compile_directory(input_dir, output_file, enable_pii_masking=True)

# Compilation with quality filtering
# compile_directory(input_dir, output_file, min_quality=0.3)


# ─────────────────────────────────────────────
# Step 2: Query the knowledge base
# ─────────────────────────────────────────────
from aura.rag import AuraRAGLoader

loader = AuraRAGLoader(output_file)
print(f"📦 Loaded {len(loader)} documents")

# Get text for a specific document
doc_ids = loader.get_all_ids()
if doc_ids:
    text = loader.get_text_by_id(doc_ids[0])
    print(f"\n📄 First document ({doc_ids[0]}):")
    print(f"   {text[:200]}...")

# Filter documents
pdf_docs = loader.filter_by_extension(".pdf")
print(f"\n📄 PDFs: {len(pdf_docs)}")

# Iterate all documents
for doc_id, text, meta in loader.iterate_texts():
    source = meta.get("source", doc_id)
    print(f"  - {source}: {len(text)} chars")

loader.close()


# ─────────────────────────────────────────────
# Step 3: Use Agent Memory
# ─────────────────────────────────────────────
from aura.memory import AuraMemoryOS

memory = AuraMemoryOS()

# Write to different memory tiers
memory.write("fact", "The auth module uses JWT tokens", source="code-review")
memory.write("episodic", "Discussed deployment strategy with the team")
memory.write("pad", "TODO: check CORS configuration")

# Query memory
results = memory.query("auth")
for entry in results:
    print(f"  [{entry.tier}] {entry.content}")

# Check memory usage
usage = memory.show_usage()
print(f"  Memory: {usage}")

# End session (flushes to durable shards)
memory.end_session()
