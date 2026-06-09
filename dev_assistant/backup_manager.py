from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKUP_DIR = PROJECT_ROOT / "docs" / "backups"


def create_backup(target_file: str) -> Path:
    source_path = PROJECT_ROOT / target_file

    if not source_path.exists():
        raise FileNotFoundError(f"バックアップ対象が見つかりません: {source_path}")

    if not source_path.is_file():
        raise IsADirectoryError(f"バックアップ対象がファイルではありません: {source_path}")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = target_file.replace("/", "__").replace("\\", "__")
    backup_path = BACKUP_DIR / f"{timestamp}__{safe_name}.bak"

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_path, backup_path)

    return backup_path