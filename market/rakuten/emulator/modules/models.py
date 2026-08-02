#
# emulator/models.py
#
# Emulator内部データモデル
#
# 役割：
#   ・楽天RSSエミュレーター内で使用する注文状態を保持
#   ・Engine側のOrderとは独立して管理する
#

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class EmulatorOrder:

    #
    # エミュレーター管理用注文データ
    #

    # Ordersシート注文ID
    #  Engine側で発行された注文識別子
    order_id: str

    # 銘柄コード
    symbol: str

    # 銘柄名称
    name: str

    # 売買
    side: str

    # 数量
    quantity: int

    #
    # 注文価格
    #
    # LIMIT:
    #   指値価格
    #
    # MARKET:
    #   None
    #
    price: float | None

    #
    # 約定価格
    #
    # RssExecutionListから取得
    #
    fill_price: float | None = None

    # 内部状態
    #  PROCESSING: 約定処理待ち
    #  FILLED: 約定完了
    #  SCENARIO: 価格シナリオ実行中
    status: str = "PROCESSING"

    # 登録時刻 (約定待ち時間判定用)
    created_at: datetime = field(
        default_factory=datetime.now
    )

    # RSS側注文番号（約定時生成）
    order_number: str = None
