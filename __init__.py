# -----------------------------------------------------------------------------
# Role: Exports the file block package API.
# File Name: __init__.py
# Author: Alexandre EL
# Email: alex@hackinvent.com
# Created Date: 2024-02-19
# -----------------------------------------------------------------------------

from .block import FileBlock, FileBlockError

__all__ = ["FileBlock", "FileBlockError"]
