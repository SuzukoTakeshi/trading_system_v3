#
# ui/console/components/auditor_panel.py
#

from datetime import datetime
from pathlib import Path
import random
import streamlit as st

from ui.console.auditor.auditor_messages import (
    load_auditor_messages,
)


def auditor_panel():

    with st.container(border=True):

        st.subheader("AUDITOR ROOM")

        messages = load_auditor_messages()

        auditor = messages.get(
            "auditor",
            {}
        )

        st.write(
            auditor.get("text", "")
        )

        image_path = _get_image_path()

        st.image(
            image_path,
            width="stretch",
        )

        event_text = "雨が振ってるよ"

        st.write(
            event_text
        )


from datetime import datetime
from pathlib import Path
import random
import streamlit as st


def _update_image_path():

    now = datetime.now()

    current_path = st.session_state.get(
        "auditor_image_path"
    )

    #
    # 画像パス生成条件
    #
    should_create = (
        not current_path
        or not Path(current_path).exists()
        or now.second == 0
    )

    if not should_create:
        return

    #
    # 画像一覧取得
    #
    image_dir = (
        Path(__file__).parent
        / "images"
    )

    images = [
        p
        for p in image_dir.iterdir()
        if p.suffix.lower()
        in [".png", ".jpg", ".jpeg", ".webp"]
    ]

    if not images:
        return

    #
    # 前回画像を除外
    #
    candidates = [
        p
        for p in images
        if p != current_path
    ]

    #
    # ランダムに画像パスを生成
    #
    st.session_state.auditor_image_path = random.choice(
        candidates or images
    )


def _get_image_path():

    _update_image_path()

    return st.session_state.get(
        "auditor_image_path"
    )
