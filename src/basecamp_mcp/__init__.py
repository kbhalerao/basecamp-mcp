"""Basecamp MCP Server - Connect Basecamp to Claude and other AI tools."""

__version__ = "0.1.0"
__author__ = "You"

from .server import mcp, cache
from .cache import CacheManager

__all__ = ["mcp", "cache", "CacheManager"]
