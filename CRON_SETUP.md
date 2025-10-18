# Basecamp MCP + Claude Code Integration

This directory contains scripts for automating your development workflow with Basecamp as a command interface and Claude Code as the executor.

## How It Works

1. **Cache Refresh** (`refresh_cache.py`): Periodically fetches fresh data from Basecamp and caches it locally
2. **Claude Code Trigger** (`trigger_claude_code.py`): Invokes Claude Code to process pending tasks from Basecamp
3. **Cron Runner** (`run_cron_job.sh`): Orchestrates both steps and logs the results

## Setup

### 1. Make scripts executable
```bash
chmod +x run_cron_job.sh refresh_cache.py trigger_claude_code.py
```

### 2. Create a cron job

Edit your crontab:
```bash
crontab -e
```

Add this line to run every 30 minutes:
```
*/30 * * * * /Users/kaustubh/Documents/BaseCampMCP/run_cron_job.sh
```

Or for every hour:
```
0 * * * * /Users/kaustubh/Documents/BaseCampMCP/run_cron_job.sh
```

### 3. Verify it's working

Check the logs:
```bash
tail -f /Users/kaustubh/Documents/BaseCampMCP/logs/basecamp_cron_*.log
```

Or list recent logs:
```bash
ls -lht /Users/kaustubh/Documents/BaseCampMCP/logs/
```

## Basecamp Workflow

### Creating Tasks for Claude Code

1. Open your Basecamp project (recommended: create a dedicated "Claude Code Queue" project)
2. Create a **todo** or **message** with your instruction
3. Include a prefix like `@claude-code` so Claude knows it's meant for the bot
4. Add relevant details and context

Example todo:
- Title: `@claude-code: Update API endpoints in src/api/`
- Description: `Endpoints need to handle pagination...`

### Claude Code Response

Claude Code will:
1. Read the pending instructions
2. Execute the tasks in your repository
3. Mark todos as complete or post a message reply with results
4. Include relevant context (file changes, test results, etc.)

## Environment Variables

Make sure `.env` is set up with:
```
BASECAMP_API_TOKEN=your_token_here
BASECAMP_ACCOUNT_ID=your_account_id_here
```

See `.env.example` for the template.

## Logs

All cron job activity is logged to `/Users/kaustubh/Documents/BaseCampMCP/logs/` with timestamps.

Format: `basecamp_cron_YYYY-MM-DD_HH-MM-SS.log`

## Workflow from Your Phone

1. Open Basecamp on your phone
2. Go to the "Claude Code Queue" project
3. Add a todo or post a message with instructions (prefix with `@claude-code`)
4. Wait for the next cron run (up to 30 minutes depending on your interval)
5. Check Basecamp for the results (Claude Code will update todos or reply)

## Customization

### Adjust cache refresh frequency

Edit `refresh_cache.py` to refresh only specific projects or data types.

### Adjust cron interval

Change the cron schedule in `crontab -e`:
- `*/15 * * * *` for every 15 minutes
- `*/60 * * * *` for every 60 minutes
- `0 9 * * *` for daily at 9 AM

### Customize Claude Code prompt

Edit the `prompt` variable in `trigger_claude_code.py` to change how Claude Code behaves.

## Troubleshooting

### Cron job not running
- Verify the script is executable: `ls -l run_cron_job.sh`
- Check system logs: `log stream --predicate 'eventMessage contains "cron"'` (macOS)
- Verify crontab was saved: `crontab -l`

### Cache not updating
- Check `.env` is in the repository root with correct credentials
- Run manually: `uv run python refresh_cache.py`
- Check logs in `/logs/` directory

### Claude Code not triggering
- Ensure Claude Code CLI is installed and in PATH: `which claude`
- Run manually: `uv run python trigger_claude_code.py`
- Check logs for error messages

### Permission errors
- Make sure scripts are executable: `chmod +x *.sh *.py`
- Check write permissions on logs directory: `mkdir -p logs && chmod 755 logs`
