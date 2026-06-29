#!/usr/bin/env python3
"""Show Windows drive disk usage from WSL."""

import sys
import shutil
from pathlib import Path


def bytes_to_gb(bytes_value: int) -> float:
    return bytes_value / (1024 ** 3)


def get_drive_usage(mount_point: Path):
    usage = shutil.disk_usage(mount_point)
    return {
        "mount_point": mount_point,
        "total_gb": bytes_to_gb(usage.total),
        "used_gb": bytes_to_gb(usage.used),
        "free_gb": bytes_to_gb(usage.free),
        "used_pct": (usage.used / usage.total) * 100,
    }


def print_drive_usage(mount_point: Path) -> None:
    usage = get_drive_usage(mount_point)
    print(f"Drive: {usage['mount_point']}")
    print(f"  Total : {usage['total_gb']:.2f} GB")
    print(f"  Used  : {usage['used_gb']:.2f} GB ({usage['used_pct']:.1f}%)")
    print(f"  Free  : {usage['free_gb']:.2f} GB")
    print("-" * 40)


def check_drive(mount_point: Path) -> None:
    print_drive_usage(mount_point)


def iter_windows_drives(mnt_path=Path("/mnt")):
    mnt_path = Path(mnt_path)
    if not mnt_path.exists():
        return []
    return [drive for drive in sorted(mnt_path.iterdir()) if drive.is_dir() and len(drive.name) == 1]


def main(argv=None):
    _ = argv
    mnt_path = Path("/mnt")

    if not mnt_path.exists():
        print("ERROR: /mnt directory not found. Are you running in WSL?")
        return 1

    print("Windows Drive Usage (from WSL)")
    print("=" * 40)

    for drive in iter_windows_drives(mnt_path):
        try:
            print_drive_usage(drive)
        except PermissionError:
            print(f"Drive: {drive} - Permission denied")
        except OSError as e:
            print(f"Drive: {drive} - Error: {e}")
    return 0


if __name__ == "__main__":
    sys.exit(main())