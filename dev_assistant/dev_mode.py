from enum import Enum


class DevMode(str, Enum):
    REPAIR = "repair"
    FEATURE = "feature"
    REFACTOR = "refactor"
    UPGRADE = "upgrade"


DEV_MODE_DESCRIPTIONS = {
    DevMode.REPAIR: (
        "現在の不具合修正モード。"
        "既存構造をできるだけ維持し、最小変更で直す。"
    ),
    DevMode.FEATURE: (
        "機能追加モード。"
        "既存構造に合わせつつ、必要なら新規ファイルや関数追加を許可する。"
    ),
    DevMode.REFACTOR: (
        "設計改善モード。"
        "動作を維持しながら構造整理や分離を行う。"
    ),
    DevMode.UPGRADE: (
        "アップグレードモード。"
        "ライブラリやSDKの新仕様への移行を許可する。"
    ),
}


def describe_dev_mode(mode: DevMode) -> str:
    return DEV_MODE_DESCRIPTIONS.get(mode, DEV_MODE_DESCRIPTIONS[DevMode.REPAIR])