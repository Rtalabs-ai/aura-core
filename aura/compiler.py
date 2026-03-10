# SPDX-License-Identifier: Apache-2.0
# AURA COMPILER - UNIVERSAL CONTEXT COMPILER
# Transforms raw files into queryable .aura knowledge bases

"""
Aura Compiler v0.1.0

The "Universal Context Compiler" - compiles any readable file format into
optimized .aura knowledge bases for AI agent memory and RAG.

Supported formats:
- Documents: PDF, DOCX, DOC, RTF, ODT, EPUB, TXT, PAGES, WPD
- Web/Markup: HTML, XML, JSON, JSONL, YAML, YML, TOML, MD, RST, TEX
- Data: CSV, TSV, XLSX, XLS, Parquet
- Communication: EML, MSG
- Code: Python, JavaScript, TypeScript, C/C++, Rust, Go, Java, etc.
- Config: INI, CFG, CONF, ENV, Dockerfile
"""

import os
import sys
import re
import json
import logging
import hashlib
import argparse
import fnmatch  # retained for discover_files pattern matching
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Iterator
from dataclasses import dataclass
from datetime import datetime

import numpy as np
from tqdm import tqdm

from .loader import AuraWriter
from .protocol import AuraMetadata, compute_content_hash

logger = logging.getLogger(__name__)

# =============================================================================
# FILE TYPE CATEGORIES
# =============================================================================

# Complex documents - use unstructured
UNSTRUCTURED_EXTENSIONS = {
    '.pdf', '.docx', '.doc', '.rtf', '.odt', '.epub', '.pages', '.wpd',
    '.html', '.htm', '.eml', '.msg', '.pptx', '.ppt'
}

# Data files - use pandas
DATA_EXTENSIONS = {
    '.csv', '.tsv', '.xlsx', '.xls', '.parquet'
}

# Structured text - use json/yaml parsers
STRUCTURED_EXTENSIONS = {
    '.json', '.jsonl', '.yaml', '.yml', '.toml', '.xml'
}

# Plain text/code - use simple file read
PLAINTEXT_EXTENSIONS = {
    # Markup
    '.txt', '.md', '.rst', '.tex', '.latex',
    # Python
    '.py', '.pyi', '.ipynb',
    # Web
    '.js', '.ts', '.jsx', '.tsx', '.css', '.scss', '.less',
    # Systems
    '.c', '.cpp', '.h', '.hpp', '.rs', '.go', '.java', '.kt', '.swift',
    # Scripts
    '.sh', '.bash', '.zsh', '.ps1', '.bat', '.cmd',
    # Backend
    '.sql', '.php', '.rb', '.cs', '.scala', '.r', '.lua', '.pl',
    # Config
    '.ini', '.cfg', '.conf', '.env', '.dockerfile', '.makefile',
    '.gitignore', '.editorconfig'
}

ALL_SUPPORTED_EXTENSIONS = (
    UNSTRUCTURED_EXTENSIONS | DATA_EXTENSIONS | 
    STRUCTURED_EXTENSIONS | PLAINTEXT_EXTENSIONS
)


# =============================================================================
# TEXT EXTRACTION
# =============================================================================

def extract_text_with_unstructured(filepath: Path) -> str:
    """
    Extract text from complex documents using unstructured.
    
    CRITICAL: Joins all elements into a single string (no chunking).
    """
    try:
        from unstructured.partition.auto import partition
    except ImportError:
        logger.warning("unstructured not installed. Install with: pip install 'unstructured[all-docs]'")
        # Fallback to simple read for some formats
        return extract_text_plaintext(filepath)
    
    try:
        elements = partition(filename=str(filepath))
        # CRITICAL: Join all elements - no chunking
        # The tokenizer handles windowing, not the parser
        full_text = "\n\n".join([el.text for el in elements if hasattr(el, 'text') and el.text])
        return full_text.strip()
    except Exception as e:
        logger.warning(f"unstructured failed for {filepath}: {e}")
        return ""


def extract_text_pandas(filepath: Path) -> str:
    """Extract text representation from data files using pandas."""
    try:
        import pandas as pd
    except ImportError:
        logger.warning("pandas not installed for data file parsing")
        return ""
    
    ext = filepath.suffix.lower()
    
    try:
        if ext == '.csv':
            df = pd.read_csv(filepath)
        elif ext == '.tsv':
            df = pd.read_csv(filepath, sep='\t')
        elif ext in {'.xlsx', '.xls'}:
            df = pd.read_excel(filepath)
        elif ext == '.parquet':
            df = pd.read_parquet(filepath)
        else:
            return ""
        
        # Convert to string representation
        # Include column headers and all rows
        return df.to_string(index=False)
    except Exception as e:
        logger.warning(f"pandas failed for {filepath}: {e}")
        return ""


def extract_text_structured(filepath: Path) -> str:
    """Extract text from structured formats (JSON, YAML, etc.)."""
    ext = filepath.suffix.lower()
    
    try:
        content = filepath.read_text(encoding='utf-8', errors='replace')
        
        if ext == '.jsonl':
            # Parse each line as JSON, extract text-like fields
            lines = []
            for line in content.strip().split('\n'):
                if line.strip():
                    try:
                        obj = json.loads(line)
                        lines.append(_extract_text_from_json(obj))
                    except json.JSONDecodeError:
                        lines.append(line)
            return '\n'.join(lines)
        
        elif ext == '.json':
            try:
                obj = json.loads(content)
                return _extract_text_from_json(obj)
            except json.JSONDecodeError:
                return content
        
        elif ext in {'.yaml', '.yml'}:
            try:
                import yaml
                obj = yaml.safe_load(content)
                return _extract_text_from_json(obj)  # Same logic works
            except:
                return content
        
        elif ext == '.toml':
            try:
                import tomllib  # Python 3.11+
            except ImportError:
                try:
                    import toml as tomllib
                except ImportError:
                    return content
            try:
                obj = tomllib.loads(content)
                return _extract_text_from_json(obj)
            except:
                return content
        
        elif ext == '.xml':
            # Just return the raw XML for now
            return content
        
        return content
    except Exception as e:
        logger.warning(f"structured parse failed for {filepath}: {e}")
        return ""


def _extract_text_from_json(obj: Any, depth: int = 0) -> str:
    """Recursively extract text from JSON-like structures."""
    if depth > 50:  # Prevent infinite recursion
        return str(obj)
    
    if isinstance(obj, str):
        return obj
    elif isinstance(obj, dict):
        parts = []
        for key, value in obj.items():
            text = _extract_text_from_json(value, depth + 1)
            if text.strip():
                parts.append(f"{key}: {text}")
        return '\n'.join(parts)
    elif isinstance(obj, list):
        return '\n'.join(_extract_text_from_json(item, depth + 1) for item in obj)
    else:
        return str(obj)


def extract_text_plaintext(filepath: Path) -> str:
    """Extract text from plaintext/code files."""
    ext = filepath.suffix.lower()
    
    try:
        # Special handling for Jupyter notebooks
        if ext == '.ipynb':
            return _extract_notebook_cells(filepath)
        
        # Simple text read
        return filepath.read_text(encoding='utf-8', errors='replace')
    except Exception as e:
        logger.warning(f"plaintext read failed for {filepath}: {e}")
        return ""


def _extract_notebook_cells(filepath: Path) -> str:
    """Extract code and markdown cells from Jupyter notebooks."""
    try:
        content = json.loads(filepath.read_text(encoding='utf-8'))
        cells = content.get('cells', [])
        
        extracted = []
        for cell in cells:
            cell_type = cell.get('cell_type', '')
            source = cell.get('source', [])
            
            if isinstance(source, list):
                source = ''.join(source)
            
            if cell_type == 'code':
                extracted.append(f"```python\n{source}\n```")
            elif cell_type == 'markdown':
                extracted.append(source)
        
        return '\n\n'.join(extracted)
    except Exception as e:
        logger.warning(f"notebook extraction failed for {filepath}: {e}")
        return ""


def extract_text(filepath: Path) -> str:
    """
    Universal text extraction - routes to appropriate extractor.
    
    Args:
        filepath: Path to the file to extract text from
        
    Returns:
        Extracted text content
    """
    ext = filepath.suffix.lower()
    
    # Handle files without extension (Makefile, Dockerfile, etc.)
    filename_lower = filepath.name.lower()
    if ext == '':
        if filename_lower in {'makefile', 'dockerfile', 'vagrantfile', 'gemfile'}:
            return extract_text_plaintext(filepath)
        elif filename_lower in {'readme', 'license', 'changelog', 'authors'}:
            return extract_text_plaintext(filepath)
    
    # Route by extension
    if ext in UNSTRUCTURED_EXTENSIONS:
        return extract_text_with_unstructured(filepath)
    elif ext in DATA_EXTENSIONS:
        return extract_text_pandas(filepath)
    elif ext in STRUCTURED_EXTENSIONS:
        return extract_text_structured(filepath)
    elif ext in PLAINTEXT_EXTENSIONS:
        return extract_text_plaintext(filepath)
    else:
        # Try plaintext as fallback
        try:
            content = filepath.read_bytes()
            # Check if it looks like text (not binary)
            if b'\x00' in content[:8192]:  # Binary detection
                logger.debug(f"Skipping binary file: {filepath}")
                return ""
            return content.decode('utf-8', errors='replace')
        except Exception:
            return ""


# =============================================================================
# EMPHASIS & TRAINING (OMNI Platform Exclusive)
# =============================================================================
# The following features are available on the OMNI Platform:
#   - Semantic emphasis weighting (--emphasize, --weights-file)
#   - Pre-computed tokenization (input_ids, attention_mask)
#   - PyTorch DataLoaders for model training
#   - Memory promotion with weighted importance
#
# Learn more: https://rtalabs.org/omni


# =============================================================================
# PII MASKING ENGINE
# =============================================================================

class PIIMaskingEngine:
    """
    Production PII masking engine for data compliance.
    
    Detects and masks personally identifiable information in text content
    before it enters the compilation pipeline. Supports:
    - Email addresses
    - Phone numbers (North American + international)
    - Social Security Numbers (US/Canadian SIN)
    - Credit card numbers (Visa, MC, Amex, Discover)
    - IP addresses (IPv4)
    - Dates of birth (common formats)
    
    All patterns are replaced with type-tagged placeholders that preserve
    semantic meaning for downstream models while removing actual PII.
    """
    
    def __init__(self):
        self.patterns = {
            'email': (
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                '[EMAIL_REDACTED]'
            ),
            'phone': (
                r'\b(?:\+?1[-. ]?)?\(?[0-9]{3}\)?[-. ]?[0-9]{3}[-. ]?[0-9]{4}\b',
                '[PHONE_REDACTED]'
            ),
            'ssn': (
                r'\b\d{3}[-. ]?\d{2}[-. ]?\d{4}\b',
                '[SSN_REDACTED]'
            ),
            'credit_card': (
                r'\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|6(?:011|5[0-9]{2})[0-9]{12})\b',
                '[CARD_REDACTED]'
            ),
            'credit_card_spaced': (
                r'\b\d{4}[-\s]\d{4}[-\s]\d{4}[-\s]\d{4}\b',
                '[CARD_REDACTED]'
            ),
            'ipv4': (
                r'\b(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b',
                '[IP_REDACTED]'
            ),
            'dob': (
                r'\b(?:0[1-9]|1[0-2])[/\-](?:0[1-9]|[12][0-9]|3[01])[/\-](?:19|20)\d{2}\b',
                '[DOB_REDACTED]'
            )
        }
        # Pre-compile patterns for performance
        self._compiled = {
            name: (re.compile(pattern, re.IGNORECASE), replacement)
            for name, (pattern, replacement) in self.patterns.items()
        }
    
    def mask_pii(self, text: str) -> Tuple[str, int]:
        """
        Mask all PII occurrences in text.
        
        Args:
            text: Input text to sanitize
            
        Returns:
            Tuple of (masked_text, total_masks_applied)
        """
        total_masked = 0
        masked_text = text
        
        for name, (compiled_pattern, replacement) in self._compiled.items():
            masked_text, count = compiled_pattern.subn(replacement, masked_text)
            if count > 0:
                total_masked += count
                logger.debug(f"PII masked: {count} {name} occurrence(s)")
        
        return masked_text, total_masked
    
    def scan_pii(self, text: str) -> Dict[str, int]:
        """
        Scan text for PII without modifying it. Useful for auditing.
        
        Args:
            text: Input text to scan
            
        Returns:
            Dict of PII type -> count found
        """
        results = {}
        for name, (compiled_pattern, _) in self._compiled.items():
            matches = compiled_pattern.findall(text)
            if matches:
                results[name] = len(matches)
        return results


# =============================================================================
# QUALITY FILTERING
# =============================================================================

class QualityFilter:
    """
    Domain-aware quality assessment for content filtering.
    
    Evaluates text quality using multiple heuristics tailored to the
    content's domain. Data that falls below the threshold is excluded
    from the compiled output to improve model training quality.
    
    Quality dimensions:
    - Textual coherence (alpha ratio, word length distribution)
    - Structural integrity (bracket balance, formatting)
    - Domain relevance (domain-specific keyword density)
    - Information density (sentence count, unique words)
    """
    
    def __init__(self, min_score: float = 0.3):
        self.min_score = min_score
    
    def assess(self, text: str, domain: str = '') -> float:
        """
        Assess content quality on a 0.0-1.0 scale.
        
        Routes to domain-specific scoring when domain is recognized,
        otherwise uses general language quality assessment.
        
        Args:
            text: Content to evaluate
            domain: Domain hint (e.g., 'financial', 'technical', 'legal')
            
        Returns:
            Float quality score between 0.0 and 1.0
        """
        if not text or len(text) < 10:
            return 0.0
        
        # Detect domain if not provided
        if not domain:
            domain = self._detect_domain(text)
        
        # Route to domain-specific scorer
        if domain in ('financial', 'banking', 'accounting'):
            return self._assess_financial(text)
        elif domain in ('technical', 'engineering', 'code'):
            return self._assess_technical(text)
        elif domain in ('structured', 'json', 'csv', 'xml'):
            return self._assess_structured(text)
        else:
            return self._assess_general(text)
    
    def _assess_general(self, text: str) -> float:
        """General language quality assessment."""
        words = text.split()
        if not words:
            return 0.0
        
        alpha_ratio = sum(c.isalpha() for c in text) / max(len(text), 1)
        avg_word_len = sum(len(w) for w in words) / len(words)
        word_len_score = min(avg_word_len / 8.0, 1.0)
        
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        sentence_score = min(len(sentences) / 5.0, 1.0)
        unique_ratio = len(set(w.lower() for w in words)) / max(len(words), 1)
        
        repetition_penalty = 0.0
        if len(words) > 20:
            word_freq = {}
            for w in words:
                word_freq[w.lower()] = word_freq.get(w.lower(), 0) + 1
            max_freq = max(word_freq.values())
            if max_freq / len(words) > 0.15:
                repetition_penalty = 0.2
        
        quality = (
            alpha_ratio * 0.30 +
            word_len_score * 0.20 +
            sentence_score * 0.20 +
            unique_ratio * 0.30
        ) - repetition_penalty
        
        return max(0.0, min(quality, 1.0))
    
    def _assess_financial(self, text: str) -> float:
        """Quality assessment for financial/banking documents."""
        base = self._assess_general(text)
        
        financial_terms = [
            'balance', 'transaction', 'payment', 'deposit', 'withdrawal',
            'account', 'statement', 'interest', 'fee', 'credit', 'debit',
            'invoice', 'revenue', 'expense', 'profit', 'loss', 'tax',
            'quarterly', 'annual', 'fiscal', 'budget', 'forecast'
        ]
        text_lower = text.lower()
        term_hits = sum(1 for term in financial_terms if term in text_lower)
        domain_score = min(term_hits / 4.0, 1.0)
        
        num_ratio = sum(c.isdigit() or c in '$.,%' for c in text) / max(len(text), 1)
        num_score = min(num_ratio * 5.0, 1.0)
        
        return base * 0.5 + domain_score * 0.30 + num_score * 0.20
    
    def _assess_technical(self, text: str) -> float:
        """Quality assessment for technical/engineering documents."""
        base = self._assess_general(text)
        
        tech_terms = [
            'function', 'class', 'method', 'variable', 'parameter',
            'api', 'endpoint', 'request', 'response', 'database',
            'server', 'client', 'protocol', 'algorithm', 'module',
            'component', 'interface', 'implementation', 'configuration'
        ]
        text_lower = text.lower()
        term_hits = sum(1 for term in tech_terms if term in text_lower)
        domain_score = min(term_hits / 4.0, 1.0)
        
        code_indicators = sum(1 for c in text if c in '{}[]();=<>/\\')
        code_score = min(code_indicators / max(len(text), 1) * 20.0, 1.0)
        
        return base * 0.4 + domain_score * 0.35 + code_score * 0.25
    
    def _assess_structured(self, text: str) -> float:
        """Quality assessment for structured data (JSON, CSV, XML)."""
        balanced = self._check_bracket_balance(text)
        balance_score = 1.0 if balanced else 0.5
        
        has_structure = any(c in text for c in '{}[]<>=",')
        structure_score = 1.0 if has_structure else 0.3
        
        lines = [l for l in text.split('\n') if l.strip()]
        line_score = min(len(lines) / 10.0, 1.0)
        
        return balance_score * 0.4 + structure_score * 0.35 + line_score * 0.25
    
    def _detect_domain(self, text: str) -> str:
        """Auto-detect content domain from text features."""
        text_lower = text.lower()
        
        financial_signals = ['balance', 'transaction', 'payment', 'account', 'invoice']
        tech_signals = ['function', 'class', 'api', 'server', 'database']
        structured_signals = ['{', '[', '<', 'xml', 'json']
        
        fin_score = sum(1 for s in financial_signals if s in text_lower)
        tech_score = sum(1 for s in tech_signals if s in text_lower)
        struct_score = sum(1 for s in structured_signals if s in text_lower)
        
        scores = {'financial': fin_score, 'technical': tech_score, 'structured': struct_score}
        best = max(scores, key=scores.get)
        
        return best if scores[best] >= 2 else 'general'
    
    def _check_bracket_balance(self, text: str) -> bool:
        """Check if brackets/braces/parens are balanced."""
        stack = []
        pairs = {'(': ')', '[': ']', '{': '}'}
        
        for char in text:
            if char in pairs:
                stack.append(pairs[char])
            elif char in pairs.values():
                if not stack or stack.pop() != char:
                    return False
        
        return len(stack) == 0


# =============================================================================
# COMPILER
# =============================================================================

@dataclass
class CompileStats:
    """Statistics from a compilation run."""
    total_files: int = 0
    processed_files: int = 0
    skipped_files: int = 0
    failed_files: int = 0
    total_tokens: int = 0
    truncated_files: int = 0
    pii_masked: int = 0
    quality_filtered: int = 0


def discover_files(input_dir: Path, recursive: bool = True) -> Iterator[Path]:
    """Discover all supported files in a directory."""
    if recursive:
        pattern = '**/*'
    else:
        pattern = '*'
    
    for filepath in input_dir.glob(pattern):
        if filepath.is_file():
            ext = filepath.suffix.lower()
            filename = filepath.name.lower()
            
            # Check extension or special filenames
            if ext in ALL_SUPPORTED_EXTENSIONS:
                yield filepath
            elif filename in {'makefile', 'dockerfile', 'vagrantfile', 'gemfile', 
                             'readme', 'license', 'changelog', 'authors'}:
                yield filepath


def compile_directory(
    input_dir: str,
    output_path: str,
    recursive: bool = True,
    skip_empty: bool = True,
    show_progress: bool = True,
    enable_pii_masking: bool = False,
    min_quality_score: float = 0.0,
    domain: str = ''
) -> CompileStats:
    """
    Compile a directory of files into an .aura archive.
    
    Stores raw text as numpy byte arrays for instant RAG retrieval.
    For pre-tokenized training archives, use the OMNI Platform.
    
    Args:
        input_dir: Path to input directory
        output_path: Path to output .aura file
        recursive: Whether to search subdirectories
        skip_empty: Skip files that produce no text
        show_progress: Show progress bar
        enable_pii_masking: Mask personally identifiable information before storage
        min_quality_score: Minimum quality score (0.0-1.0) to include a file (0.0 = no filtering)
        domain: Domain hint for quality filtering (auto-detected if empty)
        
    Returns:
        CompileStats with compilation statistics
    """
    input_dir = Path(input_dir)
    output_path = Path(output_path)
    stats = CompileStats()
    
    if not input_dir.exists():
        raise FileNotFoundError(f"Input directory not found: {input_dir}")
    
    # Discover files
    files = list(discover_files(input_dir, recursive))
    stats.total_files = len(files)
    
    if stats.total_files == 0:
        logger.warning(f"No supported files found in {input_dir}")
        return stats
    
    logger.info(f"Found {stats.total_files} files to compile")
    
    # Initialize PII masker and quality filter
    pii_masker = PIIMaskingEngine() if enable_pii_masking else None
    quality_filter = QualityFilter(min_score=min_quality_score) if min_quality_score > 0.0 else None
    
    # Compile
    with AuraWriter(output_path) as writer:
        iterator = tqdm(files, desc="Compiling", disable=not show_progress)
        
        for filepath in iterator:
            try:
                # Extract text
                text = extract_text(filepath)
                
                if not text.strip():
                    if skip_empty:
                        stats.skipped_files += 1
                        continue
                    else:
                        text = f"[Empty file: {filepath.name}]"
                
                # Quality filtering
                if quality_filter:
                    quality_score = quality_filter.assess(text, domain)
                    if quality_score < min_quality_score:
                        logger.debug(f"Filtered low-quality file ({quality_score:.2f}): {filepath}")
                        stats.quality_filtered += 1
                        stats.skipped_files += 1
                        continue
                
                # PII masking
                if pii_masker:
                    text, mask_count = pii_masker.mask_pii(text)
                    if mask_count > 0:
                        stats.pii_masked += mask_count
                        logger.debug(f"Masked {mask_count} PII occurrences in {filepath.name}")
                
                # Store raw text as numpy byte array (for RAG retrieval)
                text_bytes = text.encode('utf-8')
                tensors = {
                    'raw_text': np.frombuffer(text_bytes, dtype=np.uint8).copy()
                }
                
                # Compute content hash
                content_hash = compute_content_hash(text)
                
                # Create metadata
                metadata = {
                    'source': str(filepath.relative_to(input_dir)),
                    'content_hash': content_hash,
                    'file_extension': filepath.suffix.lower(),
                    'file_size_bytes': filepath.stat().st_size,
                    'text_length': len(text),
                    'compiled_at': datetime.utcnow().isoformat() + 'Z'
                }
                
                # Include raw text in metadata for backward compatibility
                metadata['text_content'] = text
                
                # Generate unique ID
                datapoint_id = f"{content_hash[:12]}_{filepath.stem}"
                
                # Write to archive
                writer.append_datapoint(datapoint_id, tensors, metadata)
                
                stats.processed_files += 1
                stats.total_tokens += len(text.split())  # word count as proxy
                
            except Exception as e:
                logger.warning(f"Failed to process {filepath}: {e}")
                stats.failed_files += 1
    
    logger.info(f"Compilation complete: {stats.processed_files} files, "
                f"{stats.total_tokens:,} words"
                f"{f', {stats.pii_masked} PII masked' if stats.pii_masked else ''}"
                f"{f', {stats.quality_filtered} quality-filtered' if stats.quality_filtered else ''}")
    
    return stats


# =============================================================================
# CLI
# =============================================================================

def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        prog='aura',
        description='Aura: The Universal Context Compiler for AI Agent Memory',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Compile a directory into a knowledge base
    aura compile ./my_documents/ --output knowledge.aura
    
    # Compile with PII masking
    aura compile ./company_data/ --output knowledge.aura --pii-mask
    
    # Compile with quality filtering
    aura compile ./data/ --output knowledge.aura --min-quality 0.3

    # Read an existing .aura file
    aura info knowledge.aura
    
    # List memory shards
    aura memory list
    
    # Prune old memory
    aura memory prune --before 2026-01-01
"""
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Compile command
    compile_parser = subparsers.add_parser('compile', help='Compile files into .aura format')
    compile_parser.add_argument('input', type=str, help='Input directory to compile')
    compile_parser.add_argument('--output', '-o', type=str, required=True,
                               help='Output .aura file path')
    compile_parser.add_argument('--no-recursive', action='store_true',
                               help='Do not search subdirectories')
    compile_parser.add_argument('--pii-mask', action='store_true',
                               help='Mask personally identifiable information (emails, phones, SSNs, etc.)')
    compile_parser.add_argument('--min-quality', type=float, default=0.0,
                               help='Minimum quality score (0.0-1.0) to include a file (default: 0.0 = no filtering)')
    compile_parser.add_argument('--domain', type=str, default='',
                               help='Domain hint for quality filtering (e.g., financial, technical)')
    compile_parser.add_argument('--verbose', '-v', action='store_true',
                               help='Verbose output')
    
    # Info command
    info_parser = subparsers.add_parser('info', help='Show info about an .aura file')
    info_parser.add_argument('file', type=str, help='.aura file to inspect')
    
    # Memory command
    memory_parser = subparsers.add_parser('memory', help='Manage agent memory shards')
    memory_sub = memory_parser.add_subparsers(dest='memory_command', help='Memory commands')
    
    list_parser = memory_sub.add_parser('list', help='List all memory shards')
    
    prune_parser = memory_sub.add_parser('prune', help='Prune memory shards')
    prune_parser.add_argument('--before', type=str, default=None,
                             help='Delete shards older than this date (YYYY-MM-DD)')
    prune_parser.add_argument('--id', type=str, default=None,
                             help='Delete a specific shard by ID')
    
    usage_parser = memory_sub.add_parser('usage', help='Show memory storage usage')
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if getattr(args, 'verbose', False) else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    if args.command == 'compile':
        print(f"🔥 Aura Compiler v0.1.0")
        print(f"   Input:     {args.input}")
        print(f"   Output:    {args.output}")
        if args.pii_mask:
            print(f"   PII Mask:  Enabled")
        if args.min_quality > 0.0:
            print(f"   QualFilt:  min_score={args.min_quality}")
        if args.domain:
            print(f"   Domain:    {args.domain}")
        print()
        
        try:
            stats = compile_directory(
                input_dir=args.input,
                output_path=args.output,
                recursive=not args.no_recursive,
                enable_pii_masking=args.pii_mask,
                min_quality_score=args.min_quality,
                domain=args.domain
            )
            
            print()
            print(f"✅ Compilation Complete!")
            print(f"   Processed: {stats.processed_files}/{stats.total_files} files")
            print(f"   Skipped:   {stats.skipped_files} (empty/filtered)")
            print(f"   Failed:    {stats.failed_files}")
            print(f"   Words:     {stats.total_tokens:,}")
            if stats.pii_masked:
                print(f"   PII:       {stats.pii_masked} occurrences masked")
            if stats.quality_filtered:
                print(f"   Filtered:  {stats.quality_filtered} files below quality threshold")
            print(f"   Output:    {Path(args.output).absolute()}")
            
        except Exception as e:
            print(f"❌ Compilation failed: {e}")
            sys.exit(1)
    
    elif args.command == 'info':
        from .loader import AuraReader
        
        try:
            with AuraReader(args.file) as reader:
                print(f"📦 Aura Archive: {args.file}")
                print(f"   Datapoints: {len(reader)}")
                
                if len(reader) > 0:
                    first = reader[0]
                    print(f"\n   Sample datapoint:")
                    print(f"     Tensors: {list(first['tensors'].keys())}")
                    print(f"     Source:  {first['meta'].get('source', 'N/A')}")
                    text_len = first['meta'].get('text_length', 'N/A')
                    print(f"     Length:  {text_len} chars")
        
        except Exception as e:
            print(f"❌ Failed to read file: {e}")
            sys.exit(1)
    
    elif args.command == 'memory':
        from .memory import AuraMemoryOS
        
        memory = AuraMemoryOS()
        
        if args.memory_command == 'list':
            memory.list_shards()
        elif args.memory_command == 'prune':
            if args.before:
                memory.prune_shards(before_date=args.before)
            elif args.id:
                memory.prune_shards(shard_ids=[args.id])
            else:
                print("Specify --before DATE or --id SHARD_ID")
                sys.exit(1)
        elif args.memory_command == 'usage':
            memory.show_usage()
        else:
            memory_parser.print_help()
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
