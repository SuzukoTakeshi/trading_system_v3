
import pandas as pd


def make_dataframe(rows, fallback_columns):
    """取得した行データを表示用DataFrameに変換する。"""

    if not rows:
        return pd.DataFrame(columns=fallback_columns)

    data_rows = []

    for row in rows:
        if row is None:
            continue

        values = list(row)

        if all(
            value is None or str(value).strip() == ""
            for value in values
        ):
            continue

        if any(
            isinstance(value, str)
            and value.strip() == "--------"
            for value in values
        ):
            continue

        data_rows.append(values)

    if not data_rows:
        return pd.DataFrame(columns=fallback_columns)

    first_row = data_rows[0]

    has_header = (
        any(
            isinstance(value, str) and value.strip()
            for value in first_row
        )
        and all(
            value is None or isinstance(value, str)
            for value in first_row
        )
    )

    if has_header:
        columns = [
            str(value).strip()
            if value is not None
            else f"項目{i + 1}"
            for i, value in enumerate(first_row)
        ]
        data_rows = data_rows[1:]
    else:
        columns = fallback_columns

    width = len(columns)

    normalized_rows = [
        (row + [None] * width)[:width]
        for row in data_rows
    ]

    df = pd.DataFrame(
        normalized_rows,
        columns=columns,
    )

    # 数値は3桁区切りの文字列に変換する
    def format_value(value):
        if value is None or pd.isna(value):
            return ""

        if isinstance(value, bool):
            return str(value)

        if isinstance(value, (int, float)):
            return f"{value:,.10f}".rstrip("0").rstrip(".")

        return str(value).strip()

    for column in df.columns:
        df[column] = df[column].map(format_value)

    return df
