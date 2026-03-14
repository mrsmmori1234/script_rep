#!/usr/bin/env python3

"""
Show Windows drive disk usage from WSL.

This script checks disk usage for Windows-mounted drives
(e.g. /mnt/c, /mnt/d) using Python standard libraries only.
"""

import shutil
from pathlib import Path


def bytes_to_gb(bytes_value: int) -> float:
    """Convert bytes to gigabytes (GB)."""
    return bytes_value / (1024 ** 3)


def check_drive(mount_point: Path) -> None:
    """Print disk usage for a given mount point."""
    usage = shutil.disk_usage(mount_point)

    total_gb = bytes_to_gb(usage.total)
    used_gb = bytes_to_gb(usage.used)
    free_gb = bytes_to_gb(usage.free)
    used_pct = (usage.used / usage.total) * 100

    print(f"Drive: {mount_point}")
    print(f"  Total : {total_gb:.2f} GB")
    print(f"  Used  : {used_gb:.2f} GB ({used_pct:.1f}%)")
    print(f"  Free  : {free_gb:.2f} GB")
    print("-" * 40)


def main():
    """Main entry point."""
    mnt_path = Path("/mnt")

    if not mnt_path.exists():
        print("ERROR: /mnt directory not found. Are you running in WSL?")
        return

    print("Windows Drive Usage (from WSL)")
    print("=" * 40)

    # Typical Windows drives are mounted as /mnt/c, /mnt/d, etc.
    for drive in sorted(mnt_path.iterdir()):
        if drive.is_dir() and len(drive.name) == 1:
            try:
                check_drive(drive)
            except PermissionError:
                print(f"Drive: {drive} - Permission denied")
            except OSError as e:
                print(f"Drive: {drive} - Error: {e}")


if __name__ == "__main__":
    main()
