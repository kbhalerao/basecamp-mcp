#!/usr/bin/env python3
"""Basecamp MCP Server - Connect to Basecamp via Claude and other MCP clients."""

import os
import json
from datetime import datetime, timedelta
import httpx
from typing import Any
from mcp.server.fastmcp import FastMCP
from .cache import CacheManager

# Initialize the MCP server
mcp = FastMCP("Basecamp")

# Configuration
BASECAMP_API_TOKEN = os.getenv("BASECAMP_API_TOKEN")
BASECAMP_ACCOUNT_ID = os.getenv("BASECAMP_ACCOUNT_ID")
BASE_URL = f"https://3.basecampapi.com/{BASECAMP_ACCOUNT_ID}"
CACHE_TTL = 5 * 60  # 5 minutes default cache TTL

if not BASECAMP_API_TOKEN or not BASECAMP_ACCOUNT_ID:
    raise ValueError(
        "Missing BASECAMP_API_TOKEN or BASECAMP_ACCOUNT_ID environment variables"
    )

# Initialize cache manager
cache = CacheManager(db_path="basecamp_cache.db")

# Initialize HTTP client with auth
client = httpx.Client(
    headers={
        "Authorization": f"Bearer {BASECAMP_API_TOKEN}",
        "User-Agent": "Basecamp-MCP-Server/1.0",
    },
    timeout=30.0,
)


def make_request(
    method: str, 
    endpoint: str, 
    use_cache: bool = True,
    cache_ttl: int = CACHE_TTL,
    **kwargs
) -> dict[str, Any]:
    """Make authenticated requests to Basecamp API with optional caching."""
    cache_key = f"{method}:{endpoint}"
    
    # Try cache first for GET requests
    if use_cache and method == "GET":
        cached = cache.get(cache_key)
        if cached is not None:
            return cached
    
    url = f"{BASE_URL}{endpoint}"
    try:
        response = client.request(method, url, **kwargs)
        response.raise_for_status()
        result = response.json() if response.content else {}
        
        # Cache successful GET responses
        if use_cache and method == "GET":
            cache.set(cache_key, result, ttl=cache_ttl)
        
        return result
    except httpx.HTTPError as e:
        error_msg = e.response.text if hasattr(e, 'response') else str(e)
        raise RuntimeError(f"Basecamp API error: {error_msg}")


# ============================================================================
# TOOLS - Functions Claude can call
# ============================================================================

@mcp.tool()
def get_projects() -> list[dict]:
    """List all Basecamp projects. Results are cached for 5 minutes."""
    projects = make_request("GET", "/projects.json")
    return [
        {
            "id": p["id"],
            "name": p["name"],
            "status": p["status"],
            "description": p.get("description", ""),
        }
        for p in projects
    ]


@mcp.tool()
def get_project_details(project_id: int) -> dict:
    """Get detailed information about a specific project."""
    project = make_request("GET", f"/projects/{project_id}.json", cache_ttl=10*60)
    return {
        "id": project["id"],
        "name": project["name"],
        "status": project["status"],
        "description": project.get("description", ""),
        "created_at": project["created_at"],
        "updated_at": project["updated_at"],
    }


@mcp.tool()
def get_messages(project_id: int, limit: int = 50) -> list[dict]:
    """Get recent messages from a project. Results cached for 2 minutes."""
    messages = make_request(
        "GET", 
        f"/projects/{project_id}/messages.json", 
        params={"limit": limit},
        cache_ttl=2*60
    )
    return [
        {
            "id": m["id"],
            "subject": m["subject"],
            "content": m.get("content", ""),
            "creator": m["creator"]["name"],
            "created_at": m["created_at"],
        }
        for m in messages
    ]


@mcp.tool()
def get_message_with_comments(project_id: int, message_id: int) -> dict:
    """Get a specific message with all comments."""
    message = make_request("GET", f"/projects/{project_id}/messages/{message_id}.json")
    comments = make_request("GET", f"/projects/{project_id}/messages/{message_id}/comments.json")
    
    return {
        "id": message["id"],
        "subject": message["subject"],
        "content": message.get("content", ""),
        "creator": message["creator"]["name"],
        "created_at": message["created_at"],
        "comments": [
            {
                "id": c["id"],
                "content": c.get("content", ""),
                "creator": c["creator"]["name"],
                "created_at": c["created_at"],
            }
            for c in comments
        ]
    }


@mcp.tool()
def get_todos(project_id: int, list_id: int | None = None, completed: bool | None = None) -> list[dict]:
    """Get todo items from a project or specific todo list. Optionally filter by completion status."""
    if list_id:
        todos = make_request("GET", f"/projects/{project_id}/todolists/{list_id}/todos.json", cache_ttl=2*60)
    else:
        todos = make_request("GET", f"/projects/{project_id}/todos.json", cache_ttl=2*60)
    
    results = []
    for t in todos:
        if completed is not None and t["completed"] != completed:
            continue
        results.append({
            "id": t["id"],
            "title": t["title"],
            "completed": t["completed"],
            "due_on": t.get("due_on"),
            "assignee": t.get("assignee", {}).get("name") if t.get("assignee") else None,
        })
    return results


@mcp.tool()
def create_message(project_id: int, subject: str, content: str) -> dict:
    """Create a new message in a project. Clears message cache for this project."""
    payload = {
        "subject": subject,
        "content": content,
    }
    result = make_request("POST", f"/projects/{project_id}/messages.json", json=payload, use_cache=False)
    
    # Invalidate message cache
    cache.delete(f"GET:/projects/{project_id}/messages.json")
    
    return {
        "id": result["id"],
        "subject": result["subject"],
        "created_at": result["created_at"],
    }


@mcp.tool()
def update_todo(project_id: int, todo_id: int, completed: bool) -> dict:
    """Update a todo item's completion status. Clears todo cache for this project."""
    payload = {"completed": completed}
    result = make_request("PUT", f"/projects/{project_id}/todos/{todo_id}.json", json=payload, use_cache=False)
    
    # Invalidate todo cache
    cache.delete(f"GET:/projects/{project_id}/todos.json")
    
    return {
        "id": result["id"],
        "title": result["title"],
        "completed": result["completed"],
    }


@mcp.tool()
def get_schedules(project_id: int) -> list[dict]:
    """Get schedules from a project."""
    schedules = make_request("GET", f"/projects/{project_id}/schedules.json")
    return [
        {
            "id": s["id"],
            "title": s["title"],
            "starts_on": s.get("starts_on"),
            "ends_on": s.get("ends_on"),
        }
        for s in schedules
    ]


@mcp.tool()
def clear_cache() -> dict:
    """Clear all cached data. Useful for debugging or forcing fresh data."""
    count = cache.clear_all()
    return {"status": "success", "cleared_entries": count}


@mcp.tool()
def get_cache_stats() -> dict:
    """Get statistics about the cache."""
    stats = cache.get_stats()
    return stats


# ============================================================================
# RESOURCES - Data Claude can read as context
# ============================================================================

@mcp.resource("basecamp://projects")
def projects_resource() -> str:
    """All Basecamp projects as readable context."""
    projects = make_request("GET", "/projects.json")
    output = "# Basecamp Projects\n\n"
    for p in projects:
        output += f"- **{p['name']}** (ID: {p['id']}, Status: {p['status']})\n"
        if p.get("description"):
            output += f"  {p['description']}\n"
    return output


@mcp.resource("basecamp://project/{project_id}/summary")
def project_summary_resource(project_id: int) -> str:
    """Summary of a specific project including recent activity."""
    try:
        project = make_request("GET", f"/projects/{project_id}.json")
        messages = make_request("GET", f"/projects/{project_id}/messages.json", params={"limit": 5})
        todos = make_request("GET", f"/projects/{project_id}/todos.json", params={"limit": 10})
        
        output = f"# {project['name']}\n\n"
        output += f"**Status:** {project['status']}\n"
        output += f"**Created:** {project['created_at']}\n\n"
        
        if project.get("description"):
            output += f"## Description\n{project['description']}\n\n"
        
        output += "## Recent Messages\n"
        for m in messages:
            output += f"- {m['subject']} (by {m['creator']['name']})\n"
        
        output += "\n## Outstanding Todos\n"
        incomplete = [t for t in todos if not t["completed"]]
        if incomplete:
            for t in incomplete:
                output += f"☐ {t['title']}"
                if t.get("assignee"):
                    output += f" (→ {t['assignee']['name']})"
                output += "\n"
        else:
            output += "✓ All todos complete!\n"
        
        return output
    except Exception as e:
        return f"Error fetching project summary: {str(e)}"


if __name__ == "__main__":
    mcp.run()
