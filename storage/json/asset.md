# Asset Data 説明

## 概要

Asset Data は、売買システムにおける現在の資産状態を保存する。

ファイル形式は JSON。

```json
{
    "cash": 502210.0,
    "profit_loss": 0,
    "updated_at": "2026-08-08T12:18:30.952225"
}
```

---

## 項目

### cash

現在の現金残高。

#### BUY

約定金額を現金から減算する。

```text
cash -= 約定価格 × 約定数量
```

#### SELL

約定金額を現金に加算する。

```text
cash += 約定価格 × 約定数量
```

### profit_loss

確定した売買損益。

Entry Order と Exit Order の約定価格から計算する。

#### BUY → SELL

```text
profit_loss =
    (売却価格 - 購入価格) × 数量
```

#### SELL → BUY

```text
profit_loss =
    (売却価格 - 購入価格) × 数量
```

つまり、最終的には

```text
profit_loss =
    売却金額 - 購入金額
```

となる。

損益は **Exit Order が約定した時点で確定**する。

Entry Order の約定時点では損益は確定しない。

---

## profit_loss の例

### LONG

```text
BUY
2994.8円 × 100株

SELL
2996.3円 × 100株
```

の場合、

```text
2996.3 - 2994.8 = 1.5円
1.5 × 100 = +150円
```

したがって、

```json
"profit_loss": 150.0
```

となる。

---

### SHORT

```text
SELL
3000円 × 100株

BUY
2998円 × 100株
```

の場合、

```text
3000 - 2998 = 2円
2 × 100 = +200円
```

したがって、

```json
"profit_loss": 200.0
```

となる。

---

## updated_at

Asset Data が最後に更新された日時。

`ProcessAsset` がAssetを更新した際に現在日時を設定する。

```python
asset.updated_at = datetime.now()
```

保存形式は ISO 8601。

例：

```text
2026-08-08T12:18:30.952225
```

---

## 更新タイミング

Asset Data は、約定済みOrderを `ProcessAsset` が処理したときに更新される。

処理の流れ：

```text
Order
  ↓
FILLED
  ↓
ProcessAsset
  ↓
cash 更新
  ↓
profit_loss 計算
  ↓
updated_at 更新
  ↓
Asset保存
```

---

## 現在のV3における意味

現在のV3では、Asset Data は以下の3つを管理する。

| 項目          | 意味             |
| ----------- | -------------- |
| cash        | 現在の現金残高        |
| profit_loss | 確定済み売買損益       |
| updated_at  | 最終更新日時         |

TradeがEntryからExitまで完了した場合、

```text
cash
    Entryで減少
    Exitで増加

profit_loss
    Exit約定時に確定
```

となる。

---

## 注意事項

`profit_loss` は `cash` の増減とは別に管理する。

例えば、

```text
BUY  2994.8 × 100 = -299480円
SELL 2996.3 × 100 = +299630円
```

の場合、

```text
cashの増減 = +150円
profit_loss = +150円
```

となる。

ただし、`profit_loss` は売買履歴から計算可能な**確定損益の累計値**として管理する。

---

## 関連処理

Asset更新を担当するクラス：

```text
trade/process/process_asset.py
```

主な処理：

```text
process()
    Asset取得
    ↓
update_asset()
    ↓
calculate_profit_loss()
    ↓
Asset保存
    ↓
履歴保存
```

---

## 現在の初期データ例

```json
{
    "cash": 502210.0,
    "profit_loss": 0,
    "updated_at": "2026-08-08T12:18:30.952225"
}
```

この状態は、

* 現金残高：502,210円
* 株式評価額：0円
* 確定損益：0円
* 最終更新日時：2026年8月8日 12:18:30

を表す。
