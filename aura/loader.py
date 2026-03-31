# SPDX-License-Identifier: Apache-2.0
# AURA CORE - SECURE BINARY READER/WRITER
# Implements the indexed, random-access .aura format using safetensors + msgpack.
# NO PICKLE - Secure by design.

"""
Aura Binary Format Specification (v0.1.0):

The .aura file is a binary archive with the following structure:
    [Datapoint 1][Datapoint 2]...[Datapoint N][Index][Footer]

Each Datapoint:
    [meta_length: 4 bytes, uint32, little-endian]
    [tensor_length: 4 bytes, uint32, little-endian]
    [metadata: msgpack bytes]
    [tensors: safetensors bytes]

Index:
    [msgpack dict mapping ID -> (offset, meta_len, tensor_len)]

Footer:
    [index_offset: 8 bytes, uint64, little-endian]
    [magic: 4 bytes, b'AURA']
"""

import struct
import logging
from pathlib import Path
from typing import Dict, Tuple, Any, Optional, Iterator, Union
import numpy as np

try:
    import msgpack
except ImportError:
    raise ImportError("msgpack is required. Install with: pip install msgpack")

try:
    from safetensors.numpy import save as st_save, load as st_load
except ImportError:
    raise ImportError("safetensors is required. Install with: pip install safetensors")

logger = logging.getLogger(__name__)

AURA_MAGIC = b'AURA'
AURA_VERSION = 1


class AuraWriter:
    """
    Writes datapoints to a single, indexed .aura archive.
    
    Uses safetensors for tensor storage and msgpack for metadata.
    Secure by design - no pickle, no arbitrary code execution.
    
    Example:
        >>> writer = AuraWriter("training.aura")
        >>> writer.append_datapoint("doc_001", {
        ...     "input_ids": np.array([101, 2023, 102]),
        ...     "attention_mask": np.array([1, 1, 1])
        ... }, {"source": "example.txt", "emphasis_weight": 1.5})
        >>> writer.close()
    """
    
    def __init__(self, output_path: Union[str, Path]):
        """
        Initialize the AuraWriter.
        
        Args:
            output_path: Path to the output .aura file
        """
        self.output_path = Path(output_path)
        self.index: Dict[str, Tuple[int, int, int]] = {}  # id -> (offset, meta_len, tensor_len)
        self._file_handle = open(self.output_path, 'wb')
        self._closed = False
        logger.info(f"AuraWriter initialized: {self.output_path}")

    def append_datapoint(
        self,
        datapoint_id: str,
        tensors: Dict[str, np.ndarray],
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Append a single datapoint to the archive.
        
        Args:
            datapoint_id: Unique identifier for this datapoint
            tensors: Dictionary of numpy arrays (e.g., input_ids, attention_mask)
            metadata: Optional dictionary of metadata (source, labels, weight, etc.)
        """
        if self._closed:
            raise RuntimeError("Cannot write to closed AuraWriter")
        
        if datapoint_id in self.index:
            raise ValueError(f"Duplicate datapoint ID: {datapoint_id}")
        
        # Record current file position
        offset = self._file_handle.tell()
        
        # Prepare metadata (ensure it's serializable)
        meta = metadata or {}
        meta['_id'] = datapoint_id  # Store ID in metadata for verification
        
        # Serialize metadata with msgpack
        meta_bytes = msgpack.packb(meta, use_bin_type=True)
        meta_len = len(meta_bytes)
        
        # Serialize tensors with safetensors
        # Ensure all values are numpy arrays
        tensor_dict = {}
        for key, value in tensors.items():
            if isinstance(value, np.ndarray):
                tensor_dict[key] = value
            elif isinstance(value, (list, tuple)):
                tensor_dict[key] = np.array(value)
            else:
                # Skip non-tensor values (they should be in metadata)
                logger.warning(f"Skipping non-tensor value for key '{key}' in datapoint {datapoint_id}")
                continue
        
        # Save tensors to bytes
        tensor_bytes = st_save(tensor_dict)
        tensor_len = len(tensor_bytes)
        
        # Write datapoint: [meta_len][tensor_len][meta_bytes][tensor_bytes]
        self._file_handle.write(struct.pack('<I', meta_len))
        self._file_handle.write(struct.pack('<I', tensor_len))
        self._file_handle.write(meta_bytes)
        self._file_handle.write(tensor_bytes)
        
        # Update index
        self.index[datapoint_id] = (offset, meta_len, tensor_len)

    def close(self) -> None:
        """Finalize the archive by writing the index and footer."""
        if self._closed:
            return
        
        if self._file_handle:
            # Record index position
            index_offset = self._file_handle.tell()
            
            # Serialize and write index
            index_bytes = msgpack.packb(self.index, use_bin_type=True)
            self._file_handle.write(index_bytes)
            
            # Write footer: [index_offset (8 bytes)][magic (4 bytes)]
            self._file_handle.write(struct.pack('<Q', index_offset))
            self._file_handle.write(AURA_MAGIC)
            
            self._file_handle.close()
            self._file_handle = None
            self._closed = True
            
            logger.info(f"AuraWriter closed: {len(self.index)} datapoints indexed")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False

    def __del__(self):
        if not self._closed and self._file_handle:
            logger.warning("AuraWriter was not properly closed. Closing now.")
            self.close()


class AuraReader:
    """
    Reads datapoints from an indexed .aura archive with random access.
    
    Supports both iteration (streaming) and random access (by ID).
    Zero-copy loading where possible for memory efficiency.
    
    Example:
        >>> reader = AuraReader("training.aura")
        >>> print(f"Total datapoints: {len(reader)}")
        >>> 
        >>> # Random access
        >>> data = reader.read_datapoint("doc_001")
        >>> 
        >>> # Streaming iteration
        >>> for record in reader:
        ...     print(record['meta']['source'])
    """
    
    def __init__(self, archive_path: Union[str, Path]):
        """
        Initialize the AuraReader.
        
        Args:
            archive_path: Path to the .aura file to read
        """
        self.archive_path = Path(archive_path)
        if not self.archive_path.exists():
            raise FileNotFoundError(f"Aura archive not found: {archive_path}")
        
        self._file_handle = open(self.archive_path, 'rb')
        self._validate_magic()
        self.index = self._read_index()
        self.datapoint_ids = list(self.index.keys())
        
        logger.info(f"AuraReader initialized: {len(self.datapoint_ids)} datapoints")

    def _validate_magic(self) -> None:
        """Validate the file is a valid .aura archive."""
        self._file_handle.seek(-4, 2)  # Last 4 bytes
        magic = self._file_handle.read(4)
        if magic != AURA_MAGIC:
            raise ValueError(f"Invalid .aura file: magic bytes mismatch (got {magic!r})")

    def _read_index(self) -> Dict[str, Tuple[int, int, int]]:
        """Read the index from the archive footer."""
        # Read index offset (8 bytes before magic)
        self._file_handle.seek(-12, 2)
        footer = self._file_handle.read(8)
        index_offset = struct.unpack('<Q', footer)[0]
        
        # Read index
        self._file_handle.seek(index_offset)
        # Read until 12 bytes before end (footer size)
        file_size = self.archive_path.stat().st_size
        index_size = file_size - 12 - index_offset
        index_bytes = self._file_handle.read(index_size)
        
        return msgpack.unpackb(index_bytes, raw=False)

    def read_datapoint(self, datapoint_id: str) -> Dict[str, Any]:
        """
        Read a single datapoint by ID.
        
        Args:
            datapoint_id: The unique identifier of the datapoint
            
        Returns:
            Dictionary with 'tensors' and 'meta' keys
        """
        if datapoint_id not in self.index:
            raise KeyError(f"Datapoint '{datapoint_id}' not found in archive")
        
        offset, meta_len, tensor_len = self.index[datapoint_id]
        
        # Seek to datapoint
        self._file_handle.seek(offset)
        
        # Skip length headers (8 bytes)
        self._file_handle.read(8)
        
        # Read metadata
        meta_bytes = self._file_handle.read(meta_len)
        meta = msgpack.unpackb(meta_bytes, raw=False)
        
        # Read tensors
        tensor_bytes = self._file_handle.read(tensor_len)
        tensors = st_load(tensor_bytes)
        
        return {
            'tensors': tensors,
            'meta': meta
        }

    def __len__(self) -> int:
        """Return the number of datapoints in the archive."""
        return len(self.datapoint_ids)

    def __iter__(self) -> Iterator[Dict[str, Any]]:
        """Iterate over all datapoints in order."""
        for datapoint_id in self.datapoint_ids:
            yield self.read_datapoint(datapoint_id)

    def __getitem__(self, key: Union[str, int]) -> Dict[str, Any]:
        """Get a datapoint by ID or index."""
        if isinstance(key, int):
            if key < 0 or key >= len(self.datapoint_ids):
                raise IndexError(f"Index {key} out of range")
            key = self.datapoint_ids[key]
        return self.read_datapoint(key)

    def close(self) -> None:
        """Close the file handle."""
        if self._file_handle:
            self._file_handle.close()
            self._file_handle = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False

    def __del__(self):
        self.close()