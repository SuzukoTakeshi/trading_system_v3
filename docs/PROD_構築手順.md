# Trading System V3

# 本番環境（PROD）構築手順

---

## 1. 環境構成

開発環境と本番環境を完全に分離する。

```text
C:\StockProjects\
├─ trading_system_v3_dev
│   └─ 開発環境
│
└─ trading_system_v3_prod
    └─ 本番環境
```

本番環境はDEVフォルダを直接コピーせず、GitHubからcloneして構築する。

---

## 2. GitHubから本番環境をclone

PowerShellを起動。

```powershell
cd C:\StockProjects

git clone https://github.com/SuzukoTakeshi/trading_system_v3.git trading_system_v3_prod
```

本番環境へ移動。

```powershell
cd C:\StockProjects\trading_system_v3_prod
```

Git状態を確認。

```powershell
git status
```

正常な状態：

```text
On branch main
Your branch is up to date with 'origin/main'.

nothing to commit, working tree clean
```

---

## 3. Pythonバージョン確認

DEVとPRODで同じPythonバージョンを使用する。

現在のV3環境：

```text
Python 3.14.5
```

Python本体：

```text
C:\Users\supap\AppData\Local\Python\pythoncore-3.14-64\python.exe
```

---

## 4. 本番用venv作成

本番環境のルートで実行。

```powershell
cd C:\StockProjects\trading_system_v3_prod

& "C:\Users\supap\AppData\Local\Python\pythoncore-3.14-64\python.exe" -m venv venv
```

---

## 5. venv有効化

```powershell
.\venv\Scripts\Activate.ps1
```

Pythonバージョン確認。

```powershell
python --version
```

期待値：

```text
Python 3.14.5
```

使用Python確認。

```powershell
python -c "import sys; print(sys.executable)"
```

期待値：

```text
C:\StockProjects\trading_system_v3_prod\venv\Scripts\python.exe
```

---

## 6. Pythonパッケージインストール

```powershell
python -m pip install -r requirements.txt
```

現在のrequirements.txt：

```text
fastapi==0.139.2
jpholiday==1.0.3
matplotlib==3.11.1
numpy==2.5.1
pandas==3.0.3
pywin32==312
streamlit==1.60.0
streamlit-autorefresh==1.0.1
uvicorn==0.51.0
```

---

## 7. requirements.txtに不足パッケージがあった場合

本番環境で、

```text
ModuleNotFoundError: No module named 'XXXX'
```

が発生した場合は、不足パッケージをインストールする。

例：

```powershell
python -m pip install colorama
```

インストール後、バージョン確認。

```powershell
python -m pip freeze | findstr colorama
```

確認したバージョンをrequirements.txtへ追加する。

例：

```text
colorama==XXXX
```

その後、Gitへcommit / pushする。

---

## 8. Python Path設定

PRODルートでPowerShellから直接Pythonを実行する場合：

```powershell
$env:PYTHONPATH="$PWD"
```

これにより、

```text
C:\StockProjects\trading_system_v3_prod
```

がPython Pathになる。

確認例：

```powershell
python -c "from core.config_loader import Config; print(Config.instance().data)"
```

---

## 9. 本番config設定

ファイル：

```text
C:\StockProjects\trading_system_v3_prod\config\config.json
```

本番構築時は、まず安全のためSIMULATORで開始する。

```json
{
  "mode": "simulator",
  "market": "rakuten"
}
```

現在のサーバーポート：

```text
API      : 8100
Console  : 8601
Monitor  : 8602
Auditor  : 8608
```

確認：

```powershell
$env:PYTHONPATH="$PWD"

python -c "from core.config_loader import Config; c=Config.instance().data; print('mode:', c.get('mode')); print('market:', c.get('market')); print('server:', c.get('server'))"
```

---

## 10. Rakuten設定

ファイル：

```text
C:\StockProjects\trading_system_v3_prod\rakuten\config.json
```

ExcelパスはPROD環境を指定する。

```json
"excel": {
  "path": {
    "real": "C:\\StockProjects\\trading_system_v3_prod\\rakuten\\excel\\RakutenRSS_v3.xlsm",
    "simulator": "C:\\StockProjects\\trading_system_v3_prod\\rakuten\\excel\\RakutenRSS_v3_Debug.xlsm",
    "emulator": "C:\\StockProjects\\trading_system_v3_prod\\rakuten\\excel\\RakutenRSS_v3_Debug.xlsm",
    "debug": "C:\\StockProjects\\trading_system_v3_prod\\rakuten\\excel\\RakutenRSS_v3_Debug.xlsm"
  }
}
```

---

## 11. Rakuten Excel配置

本番環境：

```text
C:\StockProjects\trading_system_v3_prod\rakuten\excel
```

現在配置されているファイル：

```text
RakutenRSS_v3.xlsm
RakutenRSS_v3_Debug.xlsm
RakutenRSS_v3_Debug - コピー.xlsm
RakutenRSS_v3_Work.xlsm
RSS発注機能を利用する場合、マーケットスピード IIの環境設定.txt
```

Simulatorでは、

```text
RakutenRSS_v3_Debug.xlsm
```

を使用する。

---

## 12. ルート直下BATのROOT設定

以下のBATは、本番環境を直接指定せず、BAT自身の場所からROOTを取得する。

対象：

```text
activate_venv.bat
start_app.bat
start_auditor.bat
start_console.bat
start_monitor.bat
TradingSystem_Start.bat
TradingSystem_Stop.bat
```

設定：

```bat
set ROOT=%~dp0
set ROOT=%ROOT:~0,-1%
```

これにより、

DEV：

```text
C:\StockProjects\trading_system_v3_dev
```

PROD：

```text
C:\StockProjects\trading_system_v3_prod
```

を自動的に判別できる。

---

## 13. rakuten\start_excel.bat

`start_excel.bat` は、

```text
rakuten\
```

フォルダ内にあるため、ROOTは1階層上を指定する。

```bat
for %%I in ("%~dp0..") do set ROOT=%%~fI
```

これにより、

```text
%~dp0
↓
...\trading_system_v3_prod\rakuten
↓
..
↓
...\trading_system_v3_prod
```

となる。

その後、

```bat
set PYTHONPATH=%ROOT%
```

でPython Pathを設定する。

---

## 14. start_excel.batの動作

`start_excel.bat` はconfigからModeを取得する。

```bat
for /f %%M in ('python -c "from core.config_loader import Config; print(Config.instance().data.get('mode', 'debug'))"') do set MODE=%%M
```

さらにModeに対応するExcelパスを取得する。

```bat
for /f "delims=" %%P in ('python -c "from rakuten.config_loader import MarketConfig; from core.config_loader import Config; mode=Config.instance().data.get('mode', 'debug'); print(MarketConfig.instance().data['excel']['path'].get(mode, ''))"') do set EXCEL_PATH=%%P
```

したがって、

```text
mode = simulator
```

の場合、

```text
RakutenRSS_v3_Debug.xlsm
```

が起動される。

---

## 15. 起動確認

まずRakuten RSS Excelを起動。

```text
rakuten\start_excel.bat
```

表示例：

```text
Trading System V3 - Rakuten RSS Excel

Mode       : simulator
Excel Path : C:\StockProjects\trading_system_v3_prod\rakuten\excel\RakutenRSS_v3_Debug.xlsm
```

Excelが正常に起動することを確認する。

---

## 16. Trading System起動

ルートの、

```text
TradingSystem_Start.bat
```

を実行する。

起動対象：

```text
Rakuten RSS Excel
APP API
CONSOLE UI
MONITOR UI
AUDITOR
```

PRODでは、

```text
API      : 8100
Console  : 8601
Monitor  : 8602
Auditor  : 8608
```

を使用する。

---

## 17. Trading System停止

```text
TradingSystem_Stop.bat
```

を使用する。

APP APIのポートはconfigから取得するため、PRODでは8100が対象になる。

Streamlitも停止する。

---

## 18. 本番環境の動作確認順序

本番環境は、いきなりREALにしない。

以下の順序で確認する。

```text
DEV
 ↓
debug
 ↓ Git push
 ↓
PROD
 ↓
simulator
 ↓
十分な動作確認
 ↓
real
```

現在は、

```text
PROD = simulator
```

とする。

REALへの変更は、Simulatorで十分な検証が完了してから行う。

---

## 19. Git運用

DEVで変更：

```powershell
git add .
git commit -m "変更内容"
git push
```

PRODへ反映：

```powershell
cd C:\StockProjects\trading_system_v3_prod

git pull
```

PROD固有の設定変更は、Git管理方針に注意する。

特に、

```text
config/config.json
rakuten/config.json
```

など、本番固有設定をDEV設定で上書きしないこと。

---

## 20. 本番環境再構築手順

PRODを作り直す場合：

```powershell
cd C:\StockProjects

git clone https://github.com/SuzukoTakeshi/trading_system_v3.git trading_system_v3_prod
cd trading_system_v3_prod
```

DEVと同じPythonでvenvを作成：

```powershell
& "C:\Users\supap\AppData\Local\Python\pythoncore-3.14-64\python.exe" -m venv venv
```

有効化：

```powershell
.\venv\Scripts\Activate.ps1
```

確認：

```powershell
python --version
```

パッケージ：

```powershell
python -m pip install -r requirements.txt
```

その後、

```text
config設定
↓
Rakuten config設定
↓
Excel配置
↓
BAT確認
↓
Simulator起動
↓
動作確認
```

の順に進める。

---

# 現在の本番環境

```text
環境
  PROD

Python
  3.14.5

Mode
  simulator

Market
  rakuten

API
  8100

Console
  8601

Monitor
  8602

Auditor
  8608

Excel
  RakutenRSS_v3_Debug.xlsm
```

---

# 重要事項

### 1. DEVを直接コピーしない

PRODはGitHubからcloneする。

### 2. PythonバージョンをDEVと合わせる

現在はPython 3.14.5。

### 3. venvはPROD専用

```text
trading_system_v3_dev\venv
trading_system_v3_prod\venv
```

を分離する。

### 4. BATにDEVの絶対パスを残さない

ルート直下：

```bat
set ROOT=%~dp0
set ROOT=%ROOT:~0,-1%
```

Rakuten配下：

```bat
for %%I in ("%~dp0..") do set ROOT=%%~fI
```

### 5. ExcelもDEVとPRODを分離する

PRODではPROD側のExcelを使用する。

### 6. 本番でも最初はSIMULATOR

```text
PROD = simulator
```

で十分な検証を行う。

### 7. 不足パッケージはrequirements.txtへ反映

PRODだけに手作業でインストールして終わりにしない。

```text
install
 ↓
requirements.txt更新
 ↓
Git commit
 ↓
Git push
```

まで行い、再構築可能な状態を維持する。
