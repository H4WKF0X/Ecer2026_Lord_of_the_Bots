
#!/usr/bin/env python3
"""
run.py
------
Connects to a robot via SSH using a pre-defined ~/.ssh/config alias and
executes botball_user_program, streaming all output live back to your terminal.
 
Usage:
    python3 run.py <ssh_alias>
 
Example:
    python3 run.py bot
"""
 
import subprocess
import sys
 
REMOTE_CMD = r"./Documents/KISS/Default\ User/ECER2026_testing/bin/botball_user_program"
 
 
def main():
    if len(sys.argv) != 2:
        sys.exit(f"Usage: python3 {sys.argv[0]} <ssh_alias>")
 
    ssh_alias = sys.argv[1]
 
    print(f"[INFO]  Connecting to '{ssh_alias}' …\n{'─' * 60}")
    result = subprocess.run(["ssh", ssh_alias, REMOTE_CMD])
    print(f"{'─' * 60}")
 
    if result.returncode == 0:
        print("[INFO]  Program exited cleanly (exit code 0).")
    else:
        print(f"[WARN]  Program exited with code {result.returncode}.", file=sys.stderr)
 
    sys.exit(result.returncode)
 
 
if __name__ == "__main__":
    main()