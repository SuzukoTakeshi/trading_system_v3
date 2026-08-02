#
# market/rakuten/work/get_result.py
#
# Excel Order Sheet Test
#
# Orderシート A1取得
#

import win32com.client
import json
import os


CONFIG_FILE = (
    "market/rakuten/config/config.json"
)


def load_config():

    with open(
        CONFIG_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)



def main():

    config = load_config()


    #
    # Excel設定
    #
    excel_path = config["excel"]["path"]

    order_sheet_name = (
        config["excel"]["sheets"]["order_list"]
    )

    print(
        f"Excel : {excel_path}"
    )

    print(
        f"Sheet : {order_sheet_name}"
    )


    #
    # Excel取得
    #
    workbook = win32com.client.GetObject(
        excel_path
    )


    #
    # Sheet
    #
    sheet = workbook.Worksheets(
        order_sheet_name
    )


    #
    # A1取得
    #
    value = sheet.Range("A1").Value


    print(
        "OrderList A1 =",
        value
    )

if __name__ == "__main__":
    main()