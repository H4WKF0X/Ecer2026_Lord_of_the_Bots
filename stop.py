#!/usr/bin/env python3
"""
stop.py
-------
Connects to a robot via SSH using a pre-defined ~/.ssh/config alias and
kills any running botball_user_program process.
 
Usage:
    python3 stop.py <ssh_alias>
 
Example:
    python3 stop.py bot
"""
 
import subprocess
import sys
 
REMOTE_BINARY = "botball_user_program"
 
 
def main():
    if len(sys.argv) != 2:
        sys.exit(f"Usage: python3 {sys.argv[0]} <ssh_alias>")
 
    ssh_alias = sys.argv[1]
 
    # Try pkill first, fall back to kill + pidof
    remote_cmd = (
        f"pkill -x {REMOTE_BINARY} 2>/dev/null || "
        f"kill $(pidof {REMOTE_BINARY}) 2>/dev/null || "
        f"kill $(cat /proc/$(grep -rl {REMOTE_BINARY} /proc/*/cmdline 2>/dev/null | head -1 | cut -d/ -f3)/status 2>/dev/null | awk '/^Pid/{{print $2}}') 2>/dev/null"
    )
 
    print(f"[INFO]  Connecting to '{ssh_alias}' …")
    result = subprocess.run(["ssh", ssh_alias, remote_cmd])
 
    if result.returncode == 0:
        print(f"[INFO]  '{REMOTE_BINARY}' killed successfully.")
    else:
        print(f"[INFO]  No running '{REMOTE_BINARY}' process found (or kill failed).")
 
 
if __name__ == "__main__":
    main()