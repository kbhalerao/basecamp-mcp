#!/usr/bin/env python3
"""Debug/test script for Basecamp MCP Server."""

import os
import sys
import asyncio
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from basecamp_mcp.server import make_request, cache, BASECAMP_API_TOKEN, BASECAMP_ACCOUNT_ID


def test_basic_connection():
    """Test basic connection to Basecamp API."""
    print("🔗 Testing Basecamp API connection...")
    
    try:
        projects = make_request("GET", "/projects.json", use_cache=False)
        print(f"✓ Connected successfully!")
        print(f"✓ Found {len(projects)} projects\n")
        
        if projects:
            print("Projects:")
            for p in projects[:3]:
                print(f"  - {p['name']} (ID: {p['id']})")
            if len(projects) > 3:
                print(f"  ... and {len(projects) - 3} more")
        
        return True
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return False


def test_cache():
    """Test cache functionality."""
    print("\n📦 Testing cache...")
    
    # Clear cache first
    cache.clear_all()
    
    # Make a request (should hit API)
    print("  Making first request (API)...")
    result1 = make_request("GET", "/projects.json", cache_ttl=60)
    
    # Make same request (should hit cache)
    print("  Making second request (should be cached)...")
    result2 = make_request("GET", "/projects.json")
    
    if result1 == result2:
        print("✓ Cache working correctly\n")
    else:
        print("✗ Cache mismatch\n")
        return False
    
    # Check stats
    stats = cache.get_stats()
    print("Cache Stats:")
    print(f"  Total entries: {stats['total_entries']}")
    print(f"  Valid entries: {stats['valid_entries']}")
    print(f"  Total hits: {stats['total_hits']}")
    print(f"  Cache size: {stats['cache_size_mb']:.2f} MB")
    
    return True


def test_endpoints():
    """Test various endpoints."""
    print("\n🧪 Testing endpoints...")
    
    try:
        # Get projects
        projects = make_request("GET", "/projects.json", use_cache=False)
        if not projects:
            print("✗ No projects found")
            return False
        
        project_id = projects[0]["id"]
        print(f"  Using project: {projects[0]['name']} (ID: {project_id})")
        
        # Test each endpoint
        endpoints = [
            ("GET", f"/projects/{project_id}.json", "Project details"),
            ("GET", f"/projects/{project_id}/messages.json", "Messages"),
            ("GET", f"/projects/{project_id}/todos.json", "Todos"),
            ("GET", f"/projects/{project_id}/schedules.json", "Schedules"),
        ]
        
        for method, endpoint, label in endpoints:
            try:
                result = make_request(method, endpoint, use_cache=False)
                count = len(result) if isinstance(result, list) else 1
                print(f"  ✓ {label}: {count} items")
            except Exception as e:
                print(f"  ✗ {label}: {str(e)[:50]}")
        
        return True
    except Exception as e:
        print(f"✗ Endpoint test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 50)
    print("Basecamp MCP Server - Debug/Test Script")
    print("=" * 50)
    
    # Check credentials
    print("\n🔑 Checking credentials...")
    if not BASECAMP_API_TOKEN or not BASECAMP_ACCOUNT_ID:
        print("✗ Missing BASECAMP_API_TOKEN or BASECAMP_ACCOUNT_ID")
        print("  Set these environment variables or create a .env file")
        sys.exit(1)
    
    print(f"✓ Token set: {BASECAMP_API_TOKEN[:20]}...")
    print(f"✓ Account ID: {BASECAMP_ACCOUNT_ID}\n")
    
    # Run tests
    success = True
    success = test_basic_connection() and success
    success = test_cache() and success
    success = test_endpoints() and success
    
    # Summary
    print("=" * 50)
    if success:
        print("✓ All tests passed! Server is ready to run.")
        print("\nStart the server with:")
        print("  uv run python src/basecamp_mcp/server.py")
    else:
        print("✗ Some tests failed. Check the output above.")
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
