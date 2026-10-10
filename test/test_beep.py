
import winsound
import time

print("Beep テスト開始")

print("1000Hzで0.5秒")
winsound.Beep(1000, 120)
winsound.Beep(1000, 120)
time.sleep(1.0)

print("1120Hzで0.5秒")
winsound.Beep(1120, 120)
winsound.Beep(1120, 120)
time.sleep(1.0)

print("2000Hzで0.5秒")
winsound.Beep(2000, 120)
winsound.Beep(2000, 120)
time.sleep(1.0)

print("900Hzで0.5秒")
winsound.Beep(900, 120)
winsound.Beep(900, 120)


print("Beep テスト終了")
