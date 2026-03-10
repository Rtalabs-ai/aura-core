# SPDX-License-Identifier: Apache-2.0
# AURA PYTORCH ADAPTER (OMNI Platform Exclusive)

"""
Aura PyTorch Adapter

This module provides PyTorch DataLoaders for training with .aura files.

NOTICE: Full PyTorch training integration (AuraDataset, AuraMapDataset,
WeightedAuraSampler) is available exclusively on the OMNI Platform.

For RAG and agent memory workflows, use:
    from aura import AuraRAGLoader

For model training, visit: https://rtalabs.org/omni
"""

raise ImportError(
    "PyTorch training features (AuraDataset, WeightedAuraSampler) are available "
    "exclusively on the OMNI Platform.\n\n"
    "  For RAG workflows:  from aura.rag import AuraRAGLoader\n"
    "  For training:       https://rtalabs.org/omni\n"
)
