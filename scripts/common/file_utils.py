"""
File and directory utilities for the GitHub Profile Generator.

This module provides safe, reusable filesystem operations built on pathlib.

Features
--------
- Atomic file writing
- JSON read/write
- Text read/write
- SVG writing
- SHA256 hashing
- Directory creation
- Safe deletion
- File validation
"""

from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
from pathlib import Path
from typing import Any

from .exceptions import (
    DirectoryCreationError,
    FileOperationError,
)


# ==========================================================
# Directory Utilities
# ==========================================================


def ensure_directory(path: Path) -> Path:
    """
    Ensure that a directory exists.

    Args:
        path:
            Directory path.

    Returns:
        Path object.

    Raises:
        DirectoryCreationError
    """
    try:
        path.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise DirectoryCreationError(
            f"Unable to create directory: {path}"
        ) from exc

    return path


# ==========================================================
# File Validation
# ==========================================================


def validate_file(path: Path) -> None:
    """
    Validate that a file exists.

    Args:
        path:
            File path.

    Raises:
        FileOperationError
    """
    if not path.exists():
        raise FileOperationError(f"File does not exist: {path}")

    if not path.is_file():
        raise FileOperationError(f"Not a file: {path}")


# ==========================================================
# Atomic Writing
# ==========================================================


def atomic_write(path: Path, data: str, encoding: str = "utf-8") -> None:
    """
    Atomically write text to a file.

    This prevents partially written files if the program crashes.

    Args:
        path:
            Destination file.

        data:
            File content.

        encoding:
            File encoding.
    """
    ensure_directory(path.parent)

    try:
        with tempfile.NamedTemporaryFile(
            "w",
            delete=False,
            dir=path.parent,
            encoding=encoding,
        ) as tmp:
            tmp.write(data)
            temp_name = Path(tmp.name)

        temp_name.replace(path)

    except OSError as exc:
        raise FileOperationError(
            f"Failed writing file: {path}"
        ) from exc


# ==========================================================
# Text Files
# ==========================================================


def read_text(path: Path, encoding: str = "utf-8") -> str:
    """
    Read a UTF-8 text file.
    """
    validate_file(path)

    try:
        return path.read_text(encoding=encoding)

    except OSError as exc:
        raise FileOperationError(
            f"Unable to read file: {path}"
        ) from exc


def write_text(path: Path, content: str) -> None:
    """
    Write text using atomic writes.
    """
    atomic_write(path, content)


# ==========================================================
# JSON
# ==========================================================


def read_json(path: Path) -> dict[str, Any]:
    """
    Read a JSON file.

    Returns:
        Parsed dictionary.
    """
    return json.loads(read_text(path))


def write_json(
    path: Path,
    data: dict[str, Any],
    *,
    indent: int = 4,
) -> None:
    """
    Write JSON using atomic writes.
    """
    atomic_write(
        path,
        json.dumps(
            data,
            indent=indent,
            ensure_ascii=False,
        ),
    )


# ==========================================================
# SVG
# ==========================================================


def write_svg(path: Path, svg: str) -> None:
    """
    Save SVG content.
    """
    atomic_write(path, svg)


# ==========================================================
# Copy
# ==========================================================


def copy_file(
    source: Path,
    destination: Path,
) -> None:
    """
    Copy a file.

    Raises:
        FileOperationError
    """
    validate_file(source)

    ensure_directory(destination.parent)

    try:
        shutil.copy2(source, destination)

    except OSError as exc:
        raise FileOperationError(
            f"Unable to copy {source} -> {destination}"
        ) from exc


# ==========================================================
# Delete
# ==========================================================


def remove_file(path: Path) -> None:
    """
    Remove a file if it exists.
    """
    try:
        if path.exists():
            path.unlink()

    except OSError as exc:
        raise FileOperationError(
            f"Unable to delete {path}"
        ) from exc


def remove_directory(path: Path) -> None:
    """
    Delete a directory recursively.
    """
    try:
        if path.exists():
            shutil.rmtree(path)

    except OSError as exc:
        raise FileOperationError(
            f"Unable to delete directory {path}"
        ) from exc


# ==========================================================
# Hashing
# ==========================================================


def sha256(path: Path) -> str:
    """
    Compute SHA256 hash of a file.

    Args:
        path:
            Input file.

    Returns:
        Hex digest.
    """
    validate_file(path)

    hasher = hashlib.sha256()

    with path.open("rb") as file:
        while chunk := file.read(8192):
            hasher.update(chunk)

    return hasher.hexdigest()


# ==========================================================
# Misc Helpers
# ==========================================================


def file_size(path: Path) -> int:
    """
    Return file size in bytes.
    """
    validate_file(path)
    return path.stat().st_size


def touch(path: Path) -> None:
    """
    Create an empty file if it doesn't exist.
    """
    ensure_directory(path.parent)

    try:
        path.touch(exist_ok=True)

    except OSError as exc:
        raise FileOperationError(
            f"Unable to touch file: {path}"
        ) from exc


def list_files(
    directory: Path,
    pattern: str = "*",
) -> list[Path]:
    """
    Return sorted files matching a glob pattern.
    """
    ensure_directory(directory)

    return sorted(
        file
        for file in directory.glob(pattern)
        if file.is_file()
    )