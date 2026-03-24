#!/usr/bin/env python3
"""
build_and_upload.py
-------------------
1. Finds the most recently modified .c file inside run/ (or use the one you specify)
2. Updates build.sh so it compiles that file
3. Runs the Docker cross-compiler
4. Uploads the resulting binary to the Wombat via scp
5. Makes sure the executable flag is set on the remote file

Uses your ~/.ssh/config alias passed as a CLI argument.

Usage:
    python3 build_and_upload.py <ssh_alias>
    python3 build_and_upload.py <ssh_alias> run/my_program.c
    python3 build_and_upload.py <ssh_alias> --no-build   # skip compile, just upload

Example:
    python3 build_and_upload.py bot
    python3 build_and_upload.py bot run/sam.c
"""

import argparse
import pathlib
import stat
import subprocess
import sys
import time

# ── Configuration ─────────────────────────────────────────────────────────────
# Path on the remote with the space kept as-is (no shell escaping here —
# we pass it through subprocess so the shell never sees it).
REMOTE_DIR    = "Documents/KISS/Default User/ECER2026_testing/bin"
REMOTE_BINARY = "botball_user_program"
LOCAL_BINARY  = pathlib.Path("output/botball_user_program")
RUN_DIR       = pathlib.Path("run")
BUILD_SCRIPT  = pathlib.Path("build.sh")
DOCKER_IMAGE  = "sillyfreak/wombat-cross"


# ── SSH helpers ───────────────────────────────────────────────────────────────

def ssh_run(alias: str, remote_cmd: str):
    """Run a command on the remote host via ssh.
    The command is passed as a single string — the remote shell interprets it,
    so spaces in paths must be quoted *within* that string.
    """
    result = subprocess.run(["ssh", alias, remote_cmd])
    if result.returncode != 0:
        sys.exit(f"[ERROR] Remote command failed (exit {result.returncode}): {remote_cmd}")


# ── Build helpers ─────────────────────────────────────────────────────────────

def find_latest_c_file(run_dir: pathlib.Path) -> pathlib.Path:
    """Return the .c file in run/ that was modified most recently."""
    c_files = list(run_dir.glob("*.c"))
    if not c_files:
        sys.exit(f"[ERROR] No .c files found in '{run_dir}/'")
    latest = max(c_files, key=lambda f: f.stat().st_mtime)
    age = time.time() - latest.stat().st_mtime
    print(f"[INFO]  Most recently changed file: {latest}  ({age:.0f}s ago)")
    return latest


def resolve_c_file(run_dir: pathlib.Path, user_input: str | None) -> pathlib.Path:
    """Return the .c file to compile — either the one the user specified or the latest."""
    if user_input:
        p = pathlib.Path(user_input)
        if not p.exists():
            # Try looking inside run/ as a convenience
            p = run_dir / p.name
        if not p.exists():
            sys.exit(f"[ERROR] Source file not found: {user_input}")
        if p.suffix != ".c":
            sys.exit(f"[ERROR] Expected a .c file, got: {p}")
        print(f"[INFO]  Using specified source file: {p}")
        return p
    return find_latest_c_file(run_dir)


def write_build_script(c_file: pathlib.Path):
    """Rewrite build.sh to compile the given c_file."""
    stem   = c_file.stem
    source = f"run/{c_file.name}"

    content = f"""#!/bin/bash
set -e

COMPILER=aarch64-linux-gnu-gcc
OUTPUT_DIR=/home/kipr/output
LIB_FLAGS="-lkipr -lm -lz -lpthread"
INCLUDES="-Ilib/include"

# Source files for your library
LIB_SRCS="lib/src/config_parser.c lib/src/drive.c lib/src/servo.c"

mkdir -p $OUTPUT_DIR
cd /home/kipr

echo "Building {stem} -> botball_user_program..."
$COMPILER -Wall $INCLUDES $LIB_SRCS {source} $LIB_FLAGS -o /home/kipr/output/botball_user_program
echo "Done! Binary in output/"
"""
    BUILD_SCRIPT.write_text(content)
    BUILD_SCRIPT.chmod(BUILD_SCRIPT.stat().st_mode | stat.S_IXUSR)
    print(f"[INFO]  build.sh updated for source file: {source}")


def run_docker_build():
    """Run the Docker cross-compilation container."""
    cmd = [
        "docker", "run", "--rm",
        "-v", f"{pathlib.Path.cwd()}:/home/kipr",
        DOCKER_IMAGE,
        "bash", "/home/kipr/build.sh",
    ]
    print("[INFO]  Running Docker build …")
    result = subprocess.run(cmd, text=True)
    if result.returncode != 0:
        sys.exit(f"[ERROR] Docker build failed (exit {result.returncode})")
    print("[INFO]  Build succeeded.")


# ── Upload ────────────────────────────────────────────────────────────────────

def upload_binary(alias: str):
    """Upload the compiled binary to the Wombat via scp and ensure +x.

    Key fix: scp receives the destination as a *single* list element
    (no shell involved), so the space in 'Default User' is passed verbatim
    and does not need any escaping.
    """
    if not LOCAL_BINARY.exists():
        sys.exit(f"[ERROR] Binary not found at {LOCAL_BINARY}. Did the build succeed?")

    remote_dest = f"{alias}:{REMOTE_DIR}/{REMOTE_BINARY}"

    print(f"[INFO]  Uploading {LOCAL_BINARY} → {remote_dest} …")
    result = subprocess.run(["scp", str(LOCAL_BINARY), remote_dest])
    if result.returncode != 0:
        sys.exit(f"[ERROR] Upload failed (exit {result.returncode})")
    print("[INFO]  Upload complete.")

    # Quote the path for the remote shell (single-quotes around the whole path)
    remote_path_sh = f"'{REMOTE_DIR}/{REMOTE_BINARY}'"
    ssh_run(alias, f"chmod 755 {remote_path_sh}")
    print("[INFO]  chmod 755 applied — executable bit confirmed.")


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Build & upload Wombat program")
    parser.add_argument("alias", help="SSH config alias for the robot (e.g. 'bot')")
    parser.add_argument(
        "source",
        nargs="?",
        default=None,
        help="Path to the .c file to compile (default: most recently modified file in run/)",
    )
    parser.add_argument("--no-build", action="store_true", help="Skip compile, just upload")
    args = parser.parse_args()

    if not args.no_build:
        c_file = resolve_c_file(RUN_DIR, args.source)
        write_build_script(c_file)
        run_docker_build()

    upload_binary(args.alias)
    print("\n[DONE]  Binary deployed to Wombat successfully.")


if __name__ == "__main__":
    main()