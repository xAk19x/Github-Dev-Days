#!/usr/bin/env python3
import argparse
import platform
import shutil
import subprocess
import sys
from pathlib import Path


def detect_os():
    system = platform.system().lower()
    mapping = {
        "linux": "linux",
        "windows": "windows",
        "darwin": "macos",
    }
    return mapping.get(system, system)


def command_exists(cmd):
    return shutil.which(cmd) is not None


def run_command(command, working_dir):
    os_name = detect_os()
    command_str = " ".join(command) if isinstance(command, list) else command
    print(f"\n[{os_name}] Running: {command_str}")
    completed = subprocess.run(
        command,
        cwd=str(working_dir),
        shell=isinstance(command, str),
        check=False,
        text=True,
    )

    if completed.stdout:
        print(completed.stdout)
    if completed.stderr:
        print(completed.stderr, file=sys.stderr)

    return completed.returncode


def upgrade_node(root_dir):
    package_file = root_dir / "package.json"
    if not package_file.exists():
        return 0

    if not command_exists("npm"):
        print("npm is not installed or not in PATH. Skipping Node upgrade.")
        return 1

    steps = [
        ["npm", "install"],
        ["npm", "audit", "fix", "--force"],
        ["npm", "update"],
    ]

    for step in steps:
        result = run_command(step, root_dir)
        if result != 0:
            print(f"Node upgrade step failed: {' '.join(step)}")
            return result

    return 0


def upgrade_php(root_dir):
    composer_file = root_dir / "composer.json"
    if not composer_file.exists():
        return 0

    if not command_exists("composer"):
        print("composer is not installed or not in PATH. Skipping PHP upgrade.")
        return 1

    steps = [
        ["composer", "update", "--with-all-dependencies", "--no-interaction", "--prefer-dist"],
        ["composer", "dump-autoload", "--optimize"],
    ]

    for step in steps:
        result = run_command(step, root_dir)
        if result != 0:
            print(f"PHP upgrade step failed: {' '.join(step)}")
            return result

    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Detect the OS and upgrade Node.js and PHP dependencies to current releases."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="Repo root containing package.json and/or composer.json",
    )
    parser.add_argument("--skip-node", action="store_true", help="Skip Node.js upgrades")
    parser.add_argument("--skip-php", action="store_true", help="Skip PHP upgrades")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    os_name = detect_os()

    print(f"Detected OS: {os_name}")
    print(f"Repository root: {repo_root}")

    package_json = repo_root / "package.json"
    composer_json = repo_root / "composer.json"

    if not package_json.exists() and not composer_json.exists():
        print("No package.json or composer.json was found in the target repository.")
        return 1

    if package_json.exists() and not args.skip_node:
        print("\n=== Upgrading Node.js dependencies ===")
        rc = upgrade_node(repo_root)
        if rc != 0:
            print("Node.js upgrade failed.")
            return rc

    if composer_json.exists() and not args.skip_php:
        print("\n=== Upgrading PHP dependencies ===")
        rc = upgrade_php(repo_root)
        if rc != 0:
            print("PHP upgrade failed.")
            return rc

    print("\nDependency remediation finished successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
