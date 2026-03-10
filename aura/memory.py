# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 Auralith Inc. All rights reserved.
#
# AURA MEMORY OS - Three-Tier Persistent Memory for AI Agents
#
# This module is distributed as a pre-built component via PyPI.
# Install with: pip install auralith-aura
#
# The open-source components (compiler, RAG, loader) are available
# on GitHub: https://github.com/Rtalabs-ai/aura-core

"""
Aura Memory OS v2.1 — Three-Tier Persistent Memory for AI Agents.

Provides a cognitively-inspired memory architecture:
    /pad       - Working notepad (transient, fast writes)
    /episodic  - Session transcripts (auto-archived)
    /fact      - Verified facts (persistent, survives indefinitely)

v2.1 Performance Enhancements:
    - Temporal decay scoring (recent memories rank higher)
    - Noise filtering (blocks meta-questions and denials)
    - Entry deduplication (prevents redundant writes)
    - Bloom filters (skip irrelevant shards during query)
    - SimHash (fuzzy matching without embedding models)
    - Tiered priority scoring (facts > episodic > pad)

Install from PyPI to use:
    pip install auralith-aura

Usage:
    from aura.memory import AuraMemoryOS
    memory = AuraMemoryOS()
    memory.write("fact", "The auth module uses JWT tokens")
"""

try:
    from aura._memory import (  # noqa: F401
        AuraMemoryOS,
        MemoryEntry,
        TwoSpeedWAL,
        ShardInfo,
        BloomFilter,
        SimHash,
        ContentDedup,
    )
except ImportError:

    class AuraMemoryOS:
        """Three-Tier Memory Operating System.

        This module requires installation via PyPI:
            pip install auralith-aura

        The Memory OS is included free in the PyPI package.
        """

        def __init__(self, *args, **kwargs):
            raise ImportError(
                "\n\nAura Memory OS is included in the PyPI package.\n"
                "Install with: pip install auralith-aura\n\n"
                "Open-source components (compiler, RAG, loader) are "
                "available on GitHub.\n"
            )

    class MemoryEntry:
        pass

    class TwoSpeedWAL:
        pass

    class ShardInfo:
        pass

    class BloomFilter:
        pass

    class SimHash:
        pass

    class ContentDedup:
        pass
