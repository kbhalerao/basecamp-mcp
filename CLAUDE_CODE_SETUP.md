# Quick Start for Claude Code

## Prerequisites

1. **Set up environment variables:**
   ```bash
   # Copy the example and fill in your credentials
   cp .env.example .env
   ```
   Edit `.env` and add:
   - `BASECAMP_API_TOKEN`: Your personal access token from Basecamp
   - `BASECAMP_ACCOUNT_ID`: Your Basecamp account ID (from the URL)

2. **Install dependencies:**
   ```bash
   uv sync
   ```

3. **Test the setup:**
   ```bash
   uv run python debug.py
   ```

## Claude Code Commands

Once you have credentials set up, you can use Claude Code to:

### Run the MCP server
```
uv run python src/basecamp_mcp/server.py
```

### Run the debug/test script
```
uv run python debug.py
```

### Add new dependencies
```
uv add package_name
```

### Work with the cache
- View stats: `uv run python -c "from basecamp_mcp.cache import CacheManager; cm = CacheManager(); print(cm.get_stats())"`
- Clear cache: `sqlite3 basecamp_cache.db "DELETE FROM cache;"`

## Project Structure

- `src/basecamp_mcp/server.py` - Main MCP server with tools & resources
- `src/basecamp_mcp/cache.py` - SQLite cache layer
- `src/basecamp_mcp/__init__.py` - Package init
- `pyproject.toml` - Project config
- `debug.py` - Test script

## Next Steps

1. Set up `.env` with your Basecamp credentials
2. Run `uv sync` to install dependencies and generate `uv.lock`
3. Run `uv run python debug.py` to verify everything works
4. Run the server with `uv run python src/basecamp_mcp/server.py`
5. Integrate with Claude Desktop (see README.md for instructions)

## MCP Tools Available

- `get_projects()` - List all projects
- `get_project_details(project_id)` - Get project info
- `get_messages(project_id, limit)` - Get messages
- `get_message_with_comments(project_id, message_id)` - Get message thread
- `get_todos(project_id, list_id, completed)` - Get todos with filtering
- `create_message(project_id, subject, content)` - Create message
- `update_todo(project_id, todo_id, completed)` - Update todo
- `get_schedules(project_id)` - Get schedules
- `get_cache_stats()` - Cache statistics
- `clear_cache()` - Clear all cache

## Resources Available

- `basecamp://projects` - All projects list
- `basecamp://project/{project_id}/summary` - Project summary with activity
