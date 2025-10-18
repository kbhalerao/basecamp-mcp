#!/usr/bin/env python3
"""
Refresh Basecamp cache by calling MCP server tools.
This script is meant to be run periodically via cron to keep cached data fresh.
"""

import os
import sys
import json
from pathlib import Path

# Add src to path so we can import the MCP module
sys.path.insert(0, str(Path(__file__).parent / "src"))

from basecamp_mcp.cache import CacheManager
from basecamp_mcp.server import BasecampMCPServer
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def refresh_basecamp_cache():
    """Refresh all cached data from Basecamp API."""
    
    api_token = os.getenv("BASECAMP_API_TOKEN")
    account_id = os.getenv("BASECAMP_ACCOUNT_ID")
    
    if not api_token or not account_id:
        print("ERROR: BASECAMP_API_TOKEN or BASECAMP_ACCOUNT_ID not set", file=sys.stderr)
        sys.exit(1)
    
    try:
        # Initialize cache manager
        cache = CacheManager()
        
        # Make API calls to refresh data
        headers = {"Authorization": f"Bearer {api_token}"}
        base_url = f"https://{account_id}.basecamp.com/api/v1"
        
        with httpx.Client() as client:
            print("[refresh_cache] Fetching projects...")
            projects_resp = client.get(f"{base_url}/projects.json", headers=headers)
            projects_resp.raise_for_status()
            projects = projects_resp.json()
            
            # Cache projects
            cache.set("projects", projects, ttl=300)
            print(f"[refresh_cache] Cached {len(projects)} projects")
            
            # Refresh messages and todos for each project
            for project in projects:
                project_id = project["id"]
                print(f"[refresh_cache] Fetching data for project {project_id}...")
                
                # Get project details
                details_resp = client.get(f"{base_url}/projects/{project_id}.json", headers=headers)
                if details_resp.status_code == 200:
                    cache.set(f"project_details_{project_id}", details_resp.json(), ttl=600)
                
                # Get messages
                try:
                    messages_resp = client.get(f"{base_url}/projects/{project_id}/messages.json", headers=headers)
                    if messages_resp.status_code == 200:
                        cache.set(f"messages_{project_id}", messages_resp.json(), ttl=120)
                        print(f"[refresh_cache] Cached messages for project {project_id}")
                except Exception as e:
                    print(f"[refresh_cache] Warning: Could not fetch messages: {e}", file=sys.stderr)
                
                # Get todos
                try:
                    todos_resp = client.get(f"{base_url}/projects/{project_id}/todos.json", headers=headers)
                    if todos_resp.status_code == 200:
                        cache.set(f"todos_{project_id}", todos_resp.json(), ttl=120)
                        print(f"[refresh_cache] Cached todos for project {project_id}")
                except Exception as e:
                    print(f"[refresh_cache] Warning: Could not fetch todos: {e}", file=sys.stderr)
        
        print("[refresh_cache] Cache refresh complete")
        stats = cache.get_stats()
        print(f"[refresh_cache] Cache stats: {json.dumps(stats, indent=2)}")
        
        return 0
        
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(refresh_basecamp_cache())
