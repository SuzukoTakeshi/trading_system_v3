#
# ui/utils/formatters.py
#
# UI共通フォーマッタ
#

from datetime import datetime


# ==================================================
# datetime
# ==================================================

def fmt_dt(dt):

    if dt is None:
        return ""

    if isinstance(dt, str):

        try:
            dt = datetime.fromisoformat(
                dt.replace("Z", "+00:00")
            )

        except Exception:
            return ""

    return dt.strftime(
        "%Y-%m-%d %H:%M:%S"
    )


WEEKDAYS_JA = ["月", "火", "水", "木", "金", "土", "日"]

def format_datetime_jp(value) -> str:
    """
    日時を日本語曜日付きで表示する。

    datetime / ISO形式文字列に対応。

    例:
        2026/08/10(月) 16:35:48
    """

    if isinstance(value, str):
        value = datetime.fromisoformat(value)

    return (
        f"{value:%Y/%m/%d}"
        f"({WEEKDAYS_JA[value.weekday()]}) "
        f"{value:%H:%M:%S}"
    )


# ==================================================
# Price
# ==================================================

def fmt_price(x, currency="¥"):

    if x is None:
        return ""

    return f"{currency}{x:,.2f}"


# ==================================================
# Money
# ==================================================

def fmt_money(x, currency="¥"):

    if x is None:
        return ""

    return f"{currency}{x:,.0f}"


# ==================================================
# Integer
# ==================================================

def fmt_int(x):

    if x is None:
        return ""

    return f"{int(x):,}"


# ==================================================
# Percentage
# ==================================================

def fmt_pct(x):

    if x is None:
        return ""

    return f"{x:.2f}%"


# ==================================================
# Number
# ==================================================

def fmt_number(
    x,
    digits=2,
    empty="--"
):

    if x is None:
        return empty

    return f"{x:,.{digits}f}"


# ==================================================
# Duration
# ==================================================

def fmt_duration(seconds):

    if seconds is None:
        return ""

    seconds = int(seconds)

    if seconds < 60:
        return f"{seconds}s"

    minutes, sec = divmod(
        seconds,
        60
    )

    if minutes < 60:
        return f"{minutes}m {sec:02d}s"

    hours, minutes = divmod(
        minutes,
        60
    )

    return f"{hours}h {minutes:02d}m"


# ==================================================
# R
# ==================================================

def fmt_r(r):

    if r is None:
        return ""

    return f"{r:.2f}R"