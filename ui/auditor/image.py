#
# ui/auditor/image.py
#
# Auditor Image
#

from datetime import datetime
from pathlib import Path
import random


def get_image_path(current_path=None):

    now = datetime.now()

    # 画像パス生成条件
    should_create = (
        not current_path
        or not Path(current_path).exists()
        or now.second == 0
    )

    if not should_create:
        return current_path

    # 画像一覧取得
    image_dir = Path("ui/auditor/random_images")

    if not image_dir.exists():
        return current_path

    images = [
        p
        for p in image_dir.iterdir()
        if p.suffix.lower()
        in [".png", ".jpg", ".jpeg", ".webp"]
    ]

    if not images:
        return current_path

    # 前回画像を除外
    candidates = [
        p
        for p in images
        if p != current_path
    ]

    # ランダムに画像パスを生成
    return random.choice(
        candidates or images
    )