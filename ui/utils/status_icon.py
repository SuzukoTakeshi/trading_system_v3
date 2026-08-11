#
# ui/utils/status_icon.py
#
# Trade状態表示アイコン共通
#


def state_icon(state: str):

    mapping = {

        "created":
            "⚪ 作成",

        "entry_wait":
            "🟨 ENTRY待機",

        "entry_pullback":
            "🟨 押し込み確認",

        "entry_reversal":
            "🟨 反転確認",

        "order_request":
            "🔵 注文中",

        "order_wait":
            "🔵 約定待ち",

        "trailing":
            "🟢 保有管理",

        "exit_create":
            "🟠 決済注文",

        "exit_wait":
            "🟠 決済待ち",

        "completed":
            "⬜ 完了",

        "canceled":
            "⚪ 取消",

        "error":
            "🔴 異常",

    }

    return mapping.get(
        state,
        state
    )