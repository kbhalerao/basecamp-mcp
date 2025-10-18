#!/usr/bin/env python3
"""
Trigger Claude Code to process pending Basecamp tasks.
This script is called after cache refresh to have Claude Code handle any pending work.
"""

import subprocess
import sys
import os
from pathlib import Path

def trigger_claude_code():
    """Trigger Claude Code to process pending Basecamp instructions."""
    
    repo_path = Path(__file__).parent
    
    # The prompt Claude Code will execute
    prompt = """
    I need you to check Basecamp for any pending tasks or instructions and execute them.
    
    Steps:
    1. Use the Basecamp MCP to get all projects and look for a "Claude Code Queue" or similar project
    2. Check for any uncompleted todos or recent messages that are instructions for you
    3. Look for items marked with a prefix like "@claude-code" or similar
    4. Execute each pending instruction
    5. Mark completed items as done in Basecamp or post a reply indicating completion
    
    Only process items that are clearly marked as instructions for you. Don't process general project discussions.
    """
    
    try:
        print("[trigger_claude_code] Starting Claude Code to process pending tasks...")
        
        # Run Claude Code with the prompt
        result = subprocess.run(
            ["claude", "code", "--dangerously-skip-permissions"],
            input=prompt.encode(),
            cwd=str(repo_path),
            capture_output=True,
            timeout=3600  # 1 hour timeout
        )
        
        print(result.stdout.decode())
        if result.stderr:
            print(result.stderr.decode(), file=sys.stderr)
        
        if result.returncode != 0:
            print(f"[trigger_claude_code] Claude Code exited with code {result.returncode}", file=sys.stderr)
            return 1
        
        print("[trigger_claude_code] Claude Code processing complete")
        return 0
        
    except subprocess.TimeoutExpired:
        print("[trigger_claude_code] Claude Code process timed out", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(trigger_claude_code())
