import json
import os
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path


def collect_system_info() -> dict:
    """Collect system information using only the Python standard library."""
    return {
        "python_version": sys.version,
        "python_version_short": platform.python_version(),
        "operating_system": platform.platform(),
        "os_name": os.name,
        "current_working_directory": str(Path.cwd()),
        "cpu_count": os.cpu_count(),
        "app_env": os.environ.get("APP_ENV"),
        "script_run_time": datetime.now(timezone.utc).isoformat(),
    }


def main() -> int:
    info = collect_system_info()
    out = json.dumps(info, ensure_ascii=False, indent=2)
    try:
        print(out)
    except UnicodeEncodeError:
        sys.stdout.buffer.write(out.encode("utf-8") + b"\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
