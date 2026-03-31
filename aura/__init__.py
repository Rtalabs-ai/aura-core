"""
Aura: The Universal Context Compiler for AI Agents

Aura compiles messy raw files (PDFs, Documents, Code, Data) into a single,
optimized binary format (.aura) ready for AI agent memory and RAG.

Quick Start:
    # Compile a directory
    >>> from aura import compile_directory
    >>> compile_directory("./my_docs/", "knowledge.aura")
    
    # Load for RAG
    >>> from aura.rag import AuraRAGLoader
    >>> loader = AuraRAGLoader("knowledge.aura")
"""

__version__ = "0.2.3"
__author__ = "Auralith Inc."

from .loader import AuraReader, AuraWriter

__all__ = [
    "AuraReader",
    "AuraWriter",
    "__version__",
]

# Feature detection
_has_memory = False
try:
    from aura._memory import AuraMemoryOS as _mem_check  # noqa: F401
    _has_memory = True
except ImportError:
    pass


# Lazy imports for optional dependencies
def __getattr__(name):
    if name == "AuraRAGLoader":
        from .rag import AuraRAGLoader
        return AuraRAGLoader
    if name == "compile_directory":
        from .compiler import compile_directory
        return compile_directory
    if name == "AuraMemoryOS":
        from .memory import AuraMemoryOS
        return AuraMemoryOS
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
