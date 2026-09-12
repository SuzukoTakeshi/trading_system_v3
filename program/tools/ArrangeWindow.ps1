param(

    # ==========================================================
    # 配置対象ウィンドウタイトル
    # ==========================================================

    [Parameter(Mandatory = $true)]
    [string]$Title,



    # ==========================================================
    # 配置先モニター番号
    #
    # 1 : メイン
    # 2 : 右側
    # 3 : 左上
    # 4 : 右上
    # ==========================================================

    [int]$Monitor = 1,



    # ==========================================================
    # レイアウト
    #
    # V3
    #     縦3配置
    #
    # MAX
    #     最大化
    # ==========================================================

    [ValidateSet("V3","MAX")]
    [string]$Layout = "V3",



    # ==========================================================
    # V3配置位置
    #
    # 1
    # 2
    # 3
    # ==========================================================

    [ValidateRange(1,3)]
    [int]$Position = 1

)



# ==========================================================
# Win32 API
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


    [DllImport("user32.dll")]
    public static extern bool ShowWindow(
        IntPtr hWnd,
        int nCmdShow
    );

}
"@



# ==========================================================
# ShowWindow
#
# SW_MAXIMIZE
# ==========================================================

$SW_MAXIMIZE = 3



# ==========================================================
# 起動待機
# ==========================================================

$MaxRetry = 20
$RetryWait = 1



# ==========================================================
# モニター座標
# ==========================================================

$monitors=@{

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



if(!$monitors.ContainsKey($Monitor)){

    Write-Host ""
    Write-Host "不正なモニター番号 : $Monitor"

    exit

}



$baseX = $monitors[$Monitor].x
$baseY = $monitors[$Monitor].y



# ==========================================================
# ウィンドウ検索
# ==========================================================

function Find-WindowByTitle($keyword){

    $script:found=[IntPtr]::Zero



    $callback={

        param(
            [IntPtr]$hwnd,
            [IntPtr]$param
        )



        if([Win32]::IsWindowVisible($hwnd)){


            $sb=New-Object System.Text.StringBuilder 512



            [Win32]::GetWindowText(
                $hwnd,
                $sb,
                512
            ) | Out-Null



            $title=$sb.ToString()



            if($title -like "*$keyword*"){


                Write-Host "発見 : $title"

                $script:found=$hwnd

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
# ウィンドウ生成待機
# ==========================================================

$retry=0

while($retry -lt $MaxRetry){

    $window=Find-WindowByTitle $Title

    if($window -ne [IntPtr]::Zero){

        Write-Host ""
        Write-Host "画面確認完了"

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



if($retry -ge $MaxRetry){

    Write-Host ""
    Write-Host "=========================="
    Write-Host "画面検出タイムアウト"
    Write-Host "=========================="

    exit

}

# ==========================================================
# レイアウト設定
# ==========================================================

switch($Layout){

    # ------------------------------------------------------
    # V3
    # 縦3配置
    # ------------------------------------------------------

    "V3" {

        $Width  = 900
        $Height = 330

        switch($Position){

            1 {

                $X = $baseX
                $Y = $baseY + 0

            }

            2 {

                $X = $baseX
                $Y = $baseY + 340

            }

            3 {

                $X = $baseX
                $Y = $baseY + 680

            }

        }


        Write-Host ""
        Write-Host "移動 : $Title"
        Write-Host (
            "Monitor={0} Position={1}" -f
            $Monitor,
            $Position
        )


        [Win32]::MoveWindow(

            [IntPtr]$window,

            $X,

            $Y,

            $Width,

            $Height,

            $true

        ) | Out-Null

    }



    # ------------------------------------------------------
    # MAX
    # 最大化
    # ------------------------------------------------------
		"MAX" {

		    [Win32]::MoveWindow(
		        [IntPtr]$window,
		        $baseX,
		        $baseY,
		        1200,
		        800,
		        $true
		    )

		    [Win32]::ShowWindow(
		        [IntPtr]$window,
		        $SW_MAXIMIZE
		    )

		}

}



Write-Host ""
Write-Host "=========================="
Write-Host "配置完了"
Write-Host "=========================="
