param(
    # 配置先モニター番号
    # 1 : メイン
    # 2 : 右側
    # 3 : 左上
    # 4 : 右上
    [int]$Monitor = 1
)



# ==========================================================
# Win32 API 定義
#
# PowerShell標準ではウィンドウ移動ができないため、
# Windows API(user32.dll)を利用する。
#
# 使用:
#   EnumWindows    : 開いているウィンドウ列挙
#   GetWindowText  : タイトル取得
#   IsWindowVisible: 表示中確認
#   MoveWindow     : ウィンドウ移動・サイズ変更
#
# ==========================================================

Add-Type @"
using System;
using System.Text;
using System.Runtime.InteropServices;

public class Win32 {

    public delegate bool EnumWindowsProc(
        IntPtr hWnd,
        IntPtr lParam
    );


    [DllImport("user32.dll")]
    public static extern bool EnumWindows(
        EnumWindowsProc lpEnumFunc,
        IntPtr lParam
    );


    [DllImport("user32.dll")]
    public static extern int GetWindowText(
        IntPtr hWnd,
        StringBuilder text,
        int count
    );


    [DllImport("user32.dll")]
    public static extern bool IsWindowVisible(
        IntPtr hWnd
    );


    [DllImport("user32.dll")]
    public static extern bool MoveWindow(
        IntPtr hWnd,
        int X,
        int Y,
        int Width,
        int Height,
        bool Repaint
    );

}
"@



# ==========================================================
# 起動待機設定
#
# Streamlit / uvicorn はPythonロード時間があるため、
# 固定timeoutではなく画面生成を確認する。
#
# 最大:
#   20秒
#
# ==========================================================

$MaxRetry = 20
$RetryWait = 1



# ==========================================================
# モニター座標
#
# 環境:
#   4モニター構成
#
# 1 : メイン
# 2 : 右側
# 3 : 左上
# 4 : 右上
#
# ※座標はWindows表示設定に依存
#
# ==========================================================

$monitors = @{

    1=@{
        x=0
        y=0
    }

    2=@{
        x=1920
        y=0
    }

    3=@{
        x=0
        y=-1080
    }

    4=@{
        x=1920
        y=-1080
    }

}



# 指定モニター確認

if(!$monitors.ContainsKey($Monitor)){

    Write-Host ""
    Write-Host "不正なモニター番号 : $Monitor"
    exit
}



$baseX = $monitors[$Monitor].x
$baseY = $monitors[$Monitor].y



# ==========================================================
# ウィンドウ検索
#
# 指定したタイトル文字列を含む画面を探す。
#
# 対象:
#   ENGINE API
#   MAIN UI
#   MONITOR UI
#
# ==========================================================

function Find-WindowByTitle($keyword){


    # 毎回初期化
    $script:found = [IntPtr]::Zero



    $callback = {

        param(
            [IntPtr]$hwnd,
            [IntPtr]$param
        )



        if([Win32]::IsWindowVisible($hwnd)){


            $sb = New-Object System.Text.StringBuilder 512



            [Win32]::GetWindowText(
                $hwnd,
                $sb,
                512
            ) | Out-Null



            $title = $sb.ToString()



            if($title -like "*$keyword*"){


                Write-Host "発見 : $title"


                $script:found = $hwnd


                # 最初の一致で終了
                return $false

            }

        }


        return $true

    }



    [Win32]::EnumWindows(
        $callback,
        [IntPtr]::Zero
    ) | Out-Null



    return [IntPtr]$script:found

}



# ==========================================================
# 画面生成待機
#
# 起動直後はStreamlit等の画面が存在しないため、
# 全画面が生成されるまで再検索する。
#
# ==========================================================

$retry = 0



while($retry -lt $MaxRetry){


    $engine = Find-WindowByTitle "ENGINE API"

    $main = Find-WindowByTitle "MAIN UI"

    $monitor = Find-WindowByTitle "MONITOR UI"



    if(
        $engine -ne [IntPtr]::Zero -and
        $main -ne [IntPtr]::Zero -and
        $monitor -ne [IntPtr]::Zero
    ){

        Write-Host ""
        Write-Host "3画面確認完了"

        break
    }



    Write-Host (
        "画面待機中... {0}/{1}" -f
        ($retry + 1),
        $MaxRetry
    )



    Start-Sleep -Seconds $RetryWait


    $retry++

}



# タイムアウト処理

if($retry -ge $MaxRetry){

    Write-Host ""
    Write-Host "=========================="
    Write-Host "画面検出タイムアウト"
    Write-Host "=========================="

    exit
}



# ==========================================================
# 配置設定
#
# 縦3段:
#
# ENGINE API
# MAIN UI
# MONITOR UI
#
# サイズ:
#   幅 900
#   高さ 330
#
# ==========================================================

$windows=@(

    @{
        name="ENGINE API"
        hwnd=$engine
        y=0
    },

    @{
        name="MAIN UI"
        hwnd=$main
        y=340
    },

    @{
        name="MONITOR UI"
        hwnd=$monitor
        y=680
    }

)



# ==========================================================
# ウィンドウ移動
# ==========================================================

foreach($w in $windows){


    Write-Host "移動 : $($w.name)"



    [Win32]::MoveWindow(

        [IntPtr]$w.hwnd,

        $baseX,

        ($baseY + $w.y),

        900,

        330,

        $true

    )

}



Write-Host ""

Write-Host "=========================="

Write-Host "配置完了"

Write-Host "=========================="