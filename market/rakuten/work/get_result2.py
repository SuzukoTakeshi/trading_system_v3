#
# market/rakuten/work/get_result2.py
#
# Excel Sheet Check
#
# OrderList / OrderIDList 確認
#

import win32com.client
import json


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



def dump_sheet(
    workbook,
    sheet_name,
    range_name
):

    print()
    print("=" * 40)
    print(sheet_name)
    print("=" * 40)

    sheet = workbook.Worksheets(
        sheet_name
    )

    values = sheet.Range(
        range_name
    ).Value


    for row in values:
        print(row)



def main():

    config = load_config()


    excel_path = config["excel"]["path"]


    print(
        f"Excel : {excel_path}"
    )


    #
    # Workbook取得
    #
    workbook = win32com.client.GetObject(
        excel_path
    )


    sheets = config["excel"]["sheets"]


    #
    # OrderList
    #
    dump_sheet(
        workbook,
        sheets["order_list"],
        "A1:AD5"
    )


    #
    # OrderIDList
    #
    dump_sheet(
        workbook,
        sheets["order_id_list"],
        "A1:F10"
    )


if __name__ == "__main__":
    main()