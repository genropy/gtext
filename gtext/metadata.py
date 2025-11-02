"""Metadata management for .gtext source files.

This module handles reading and writing metadata (output paths, timestamps)
as JSON in HTML comments at the beginning of .gtext source files.
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


def read_metadata(source_path: Path) -> Dict:
    """Read metadata from a .gtext source file.

    Args:
        source_path: Path to the .gtext source file

    Returns:
        Dictionary with metadata (empty if no metadata found)
        Format: {"outputs": [{"path": "out.md", "timestamp": "..."}]}
    """
    if not source_path.exists():
        return {}

    content = source_path.read_text(encoding="utf-8")

    # Look for metadata comment at the beginning
    # Format: <!-- gtext:{"outputs":[...]} -->
    pattern = r"<!--\s*gtext:(\{.*?\})\s*-->"
    match = re.search(pattern, content, re.DOTALL)

    if match:
        try:
            metadata = json.loads(match.group(1))
            return metadata
        except json.JSONDecodeError:
            return {}

    return {}


def write_metadata(source_path: Path, metadata: Dict) -> None:
    """Write metadata to a .gtext source file.

    Updates or adds metadata comment at the beginning of the file.

    Args:
        source_path: Path to the .gtext source file
        metadata: Dictionary with metadata to save
    """
    if not source_path.exists():
        raise FileNotFoundError(f"Source file not found: {source_path}")

    content = source_path.read_text(encoding="utf-8")

    # Format metadata as compact JSON in HTML comment
    metadata_json = json.dumps(metadata, separators=(",", ":"))
    metadata_comment = f"<!-- gtext:{metadata_json} -->\n"

    # Check if metadata comment already exists
    pattern = r"<!--\s*gtext:\{.*?\}\s*-->\n?"
    if re.search(pattern, content, re.DOTALL):
        # Replace existing metadata
        new_content = re.sub(pattern, metadata_comment, content, count=1, flags=re.DOTALL)
    else:
        # Add metadata at the beginning
        new_content = metadata_comment + content

    source_path.write_text(new_content, encoding="utf-8")


def add_output(source_path: Path, output_path: Path) -> None:
    """Add an output path to the source file's metadata.

    Args:
        source_path: Path to the .gtext source file
        output_path: Path where the file was rendered
    """
    metadata = read_metadata(source_path)

    # Initialize outputs list if not present
    if "outputs" not in metadata:
        metadata["outputs"] = []

    # Convert output_path to string (relative to source if possible)
    try:
        output_str = str(output_path.relative_to(source_path.parent))
    except ValueError:
        # Not relative, use absolute
        output_str = str(output_path.absolute())

    # Check if this output already exists
    timestamp = datetime.utcnow().isoformat() + "Z"
    for output in metadata["outputs"]:
        if output["path"] == output_str:
            # Update timestamp
            output["timestamp"] = timestamp
            break
    else:
        # Add new output
        metadata["outputs"].append({"path": output_str, "timestamp": timestamp})

    # Sort by timestamp (most recent first)
    metadata["outputs"].sort(key=lambda x: x["timestamp"], reverse=True)

    write_metadata(source_path, metadata)


def get_outputs(source_path: Path) -> List[Dict]:
    """Get list of outputs for a source file.

    Args:
        source_path: Path to the .gtext source file

    Returns:
        List of output dictionaries, sorted by timestamp (most recent first)
        Each dict has "path" and "timestamp" keys
    """
    metadata = read_metadata(source_path)
    return metadata.get("outputs", [])


def get_most_recent_output(source_path: Path) -> Optional[Path]:
    """Get the most recently used output path for a source file.

    Args:
        source_path: Path to the .gtext source file

    Returns:
        Path to the most recent output, or None if no outputs recorded
    """
    outputs = get_outputs(source_path)
    if not outputs:
        return None

    # First output is most recent (list is sorted)
    output_str = outputs[0]["path"]

    # Resolve relative paths
    if not Path(output_str).is_absolute():
        return source_path.parent / output_str
    return Path(output_str)


def remove_output(source_path: Path, output_path: Path) -> bool:
    """Remove an output path from the source file's metadata.

    Args:
        source_path: Path to the .gtext source file
        output_path: Path to remove

    Returns:
        True if output was removed, False if not found
    """
    metadata = read_metadata(source_path)

    if "outputs" not in metadata:
        return False

    # Convert to string for comparison
    try:
        output_str = str(output_path.relative_to(source_path.parent))
    except ValueError:
        output_str = str(output_path.absolute())

    # Remove matching output
    original_len = len(metadata["outputs"])
    metadata["outputs"] = [o for o in metadata["outputs"] if o["path"] != output_str]

    if len(metadata["outputs"]) < original_len:
        write_metadata(source_path, metadata)
        return True

    return False
