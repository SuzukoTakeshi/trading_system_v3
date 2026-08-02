param(

    # 検索するウィンドウタイトル
    #
    # 例:
    #   ENGINE API
    #   MAIN UI
    #   MONITOR UI
    #
    [Parameter(Mandatory = $true)]
    [string]$Title

)



# ==========================================================
# CheckWindow.ps1
#
# 指定したタイトルを含むウィンドウが
# 現在存在するか確認する。
#
# 戻り値:
#
#   0 : 見つかった
#   1 : 見つからない
#
# 使用例:
#
#   powershell -File CheckWindow.ps1 "ENGINE API"
#
# ==========================================================



# ==========================================================
# Win32 API 定義
#
# EnumWindows    : 全ウィンドウ列挙
# GetWindowText  : タイトル取得
# IsWindowVisible: 表示中確認
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

}
"@



# ==========================================================
# ウィンドウ検索
#
# 指定タイトルを含む画面を探す。
#
# ==========================================================

$script:found = $false

$callback = {

    param(
        [IntPtr]$hWnd,
        [IntPtr]$lParam
    )

    if([Win32]::IsWindowVisible($hWnd)){

        $sb = New-Object System.Text.StringBuilder 512

        [Win32]::GetWindowText(
            $hWnd,
            $sb,
            512
        ) | Out-Null

        $windowTitle = $sb.ToString()

        if($windowTitle -like "*$Title*"){

            Write-Host "発見 : $windowTitle"

            $script:found = $true

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



# ==========================================================
# 終了コード
#
#   0 : 見つかった
#   1 : 見つからない
#
# ==========================================================

if($script:found){

    exit 0

}

exit 1