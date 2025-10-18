# Basecamp MCP Server

Connect your Basecamp workspace to Claude and other AI tools via the Model Context Protocol.

## Setup

### 1. Get Basecamp API Credentials

1. Go to [Basecamp](https://basecamp.com) and log in
2. Click your profile → "Settings" → "Personal access tokens" (or "Integrations & apps" → "API credentials")
3. Create a new token (it needs "all access")
4. Copy the token
5. Find your Account ID in the URL when you're in your workspace (e.g., `https://3.basecamp.com/ACCOUNT_ID`)

### 2. Set Environment Variables

```bash
export BASECAMP_API_TOKEN="your_token_here"
export BASECAMP_ACCOUNT_ID="your_account_id_here"
```

Or create a `.env` file in the project root (add to `.gitignore`):
```
BASECAMP_API_TOKEN=your_token_here
BASECAMP_ACCOUNT_ID=your_account_id_here
```

### 3. Install Dependencies

```bash
uv sync
```

### 4. Run the Server

```bash
uv run python -m basecamp_mcp.server
```

Or run it directly:
```bash
uv run python src/basecamp_mcp/server.py
```

## Features

### Tools (Functions Claude Can Call)

- **`get_projects`** - List all Basecamp projects
- **`get_project_details`** - Get detailed info about a project
- **`get_messages`** - Get recent messages from a project
- **`get_message_with_comments`** - Get a specific message with all comments
- **`get_todos`** - Get todo items (with optional filtering by completion)
- **`create_message`** - Create a new message in a project
- **`update_todo`** - Mark a todo as complete/incomplete
- **`get_schedules`** - Get schedules from a project
- **`clear_cache`** - Clear all cached data
- **`get_cache_stats`** - View cache statistics

### Resources (Data Claude Can Read)

- **`basecamp://projects`** - List of all projects
- **`basecamp://project/{project_id}/summary`** - Project summary with recent activity

### Caching

The server uses SQLite for persistent caching with TTL (Time To Live):

- **Projects**: 5 minutes cache
- **Messages**: 2 minutes cache
- **Todos**: 2 minutes cache
- **Project details**: 10 minutes cache

Use `get_cache_stats` to see cache hit rates and size, or `clear_cache` to force fresh data.

## Project Structure

```
BaseCampMCP/
├── src/
│   └── basecamp_mcp/
│       ├── __init__.py
│       ├── server.py       # Main MCP server with tools & resources
│       └── cache.py        # SQLite cache manager
├── pyproject.toml          # Project configuration
└── README.md
```

## Integration with Claude Desktop

To use with Claude Desktop:

1. Edit `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or the Windows equivalent
2. Add the server:

```json
{
  "mcpServers": {
    "basecamp": {
      "command": "uv",
      "args": ["run", "--with", "mcp", "python", "-m", "basecamp_mcp.server"],
      "cwd": "/Users/kaustubh/Documents/BaseCampMCP"
    }
  }
}
```

3. Restart Claude Desktop

## Development

### Testing the Server

```bash
# Run with verbose logging
uv run python -m basecamp_mcp.server
```

### Viewing Cache

The cache database is stored in `basecamp_cache.db` in your working directory. You can inspect it with:

```bash
sqlite3 basecamp_cache.db
sqlite> SELECT key, hits, expires_at FROM cache ORDER BY hits DESC;
```

## API Reference

### Basecamp API v1 Endpoints Used

- `GET /projects.json` - List projects
- `GET /projects/{id}.json` - Get project details
- `GET /projects/{id}/messages.json` - List messages
- `GET /projects/{id}/messages/{message_id}.json` - Get message
- `GET /projects/{id}/messages/{message_id}/comments.json` - Get comments
- `GET /projects/{id}/todos.json` - List todos
- `GET /projects/{id}/todolists/{list_id}/todos.json` - Get todos from list
- `PUT /projects/{id}/todos/{todo_id}.json` - Update todo
- `POST /projects/{id}/messages.json` - Create message
- `GET /projects/{id}/schedules.json` - List schedules

## License

MIT
