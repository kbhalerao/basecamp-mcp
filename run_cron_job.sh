#!/bin/bash
# Cron-friendly runner script that executes both cache refresh and Claude Code trigger

REPO_DIR="/Users/kaustubh/Documents/BaseCampMCP"
LOG_DIR="/Users/kaustubh/Documents/BaseCampMCP/logs"
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
LOG_FILE="$LOG_DIR/basecamp_cron_$TIMESTAMP.log"

# Create logs directory if it doesn't exist
mkdir -p "$LOG_DIR"

echo "=== Basecamp MCP Cron Job ===" >> "$LOG_FILE"
echo "Started at $(date)" >> "$LOG_FILE"

# Step 1: Refresh cache
echo "" >> "$LOG_FILE"
echo "--- Step 1: Refreshing Basecamp cache ---" >> "$LOG_FILE"
cd "$REPO_DIR"
uv run python refresh_cache.py >> "$LOG_FILE" 2>&1
REFRESH_EXIT=$?

if [ $REFRESH_EXIT -ne 0 ]; then
    echo "ERROR: Cache refresh failed with exit code $REFRESH_EXIT" >> "$LOG_FILE"
    echo "Aborting Claude Code trigger" >> "$LOG_FILE"
    exit $REFRESH_EXIT
fi

# Step 2: Trigger Claude Code
echo "" >> "$LOG_FILE"
echo "--- Step 2: Triggering Claude Code ---" >> "$LOG_FILE"
uv run python trigger_claude_code.py >> "$LOG_FILE" 2>&1
CC_EXIT=$?

if [ $CC_EXIT -ne 0 ]; then
    echo "WARNING: Claude Code trigger exited with code $CC_EXIT" >> "$LOG_FILE"
fi

echo "" >> "$LOG_FILE"
echo "Completed at $(date)" >> "$LOG_FILE"
echo "=== End of cron job ===" >> "$LOG_FILE"

exit 0
