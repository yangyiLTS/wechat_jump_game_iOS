#  -*- coding: utf-8 -*-
import pyfirmata
import time

# =======Arduino舵机控制脚本=========
#  需要Arduino先烧入StandFirmata
#  请修改串口编号为实际Arduino串口编号



# 设置舵机的高点和低点  单位：角度
# 范围 0-180°

servo_high = 45
servo_low = 37

# 修改串口编号 如果Arduino驱动正确，在Arduino IDE可以看到串口编号
serial_int = 'COM3'

# 如果是Arduino UNO 使用这一条
board = pyfirmata.Arduino(serial_int)

# 如果是Arduino Mega 使用这一条 pyfirmata库暂不支持Nano
# board = pyfirmata.ArduinoMega(serial_int)

servo_pin = board.get_pin('d:3:s') # 使用3号输出口  可以自行调整
iter8 = pyfirmata.util.Iterator(board)
iter8.start()

servo_pin.write(servo_high)
# 舵机控制函数
def arduino_servo_run(t):
    servo_pin.write(servo_low)
    time.sleep(t)
    servo_pin.write(servo_high)



