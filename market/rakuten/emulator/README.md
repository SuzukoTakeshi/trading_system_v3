# Emulator

## 概要

`emulator` は、MarketSpeed2 RSS環境を模擬するためのテスト用コンポーネント。

実際のExcel RSS接続を使用せずに、

- 株価配信
- 注文受付
- 約定処理
- OrderID生成
- 注文状態更新

をシミュレーションする。

V2では、EngineやTrade管理のテスト基盤として利用する。

---

## 役割

Emulatorは実際のBroker/RSS環境の代替として動作する。


---

## ディレクトリ構成

emulator/
│
├─ service.py
│ Emulator全体の制御
│ 外部公開インターフェース
│
├─ modules/
│ ├─ excel.py
│ │ RSS Excel環境の模擬
│ │
│ ├─ models.py
│ │ Emulator内部データモデル
│ │
│ ├─ orders.py
│ │ 注文監視・約定処理
│ │
│ └─ scenario.py
│ 株価変化シナリオ管理
│
├─ scenarios/
│ 銘柄別価格変化シナリオ
│
├─ test.py
│ Emulator
│
└─ test_order.py
   Emulator動作確認用テスト
