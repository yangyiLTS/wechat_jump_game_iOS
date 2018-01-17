感谢来自 [wangshub](https://github.com/wangshub "wangshub") 的跳跃距离算法，原项目地址：[wangshub/wechat_jump_game](https://github.com/wangshub/wechat_jump_game)

知乎专栏：[教你用Python来玩微信跳一跳](https://zhuanlan.zhihu.com/p/32452473)

----------

本项目知乎专栏：[python玩“跳一跳” iOS+Win版](https://zhuanlan.zhihu.com/p/32526110)

# 简介 #

基于OpenCV图片识别的微信跳一跳辅助，使用于ios和windows平台，硬件部分支持Raspberry Pi和Arduino。

# 基本思路 #

1. 使用iOS自带Airplay服务将游戏画面投影到电脑上。
2. 使用Pillow库截取电脑屏幕，获得游戏画面。
3. 使用OpenCV分析图片，计算出跳跃距离，乘以时间系数获得按压时间。
4. 将按压时间发送至树莓派/Arduino，树莓派/Arduino控制舵机点击手机屏幕。


# 运行环境&工具 #


- Python 3.6 in Windows
- Pillow、numpy、pyfirmata
- opencv-python
- 局域网环境
- iToools Airplayer
- 树莓派 或 arduino
- SG90 舵机
- 杜邦线、纸板
- 一小块海绵


# 原理 & 步骤 #

## 舵机 & 控制器 部分 ##

1. 拿一根杜邦线粘在舵机的摆臂上，并且固定好舵机。如图：

![](https://github.com/yangyiLTS/wechat_jump_game_iOS/raw/master/data/servo.jpg)

2. 取一小块海绵，约10mm\*10mm\*5mm，不必太精确。海绵中间挖一个小洞。大概是这样：
![](https://github.com/yangyiLTS/wechat_jump_game_iOS/raw/master/data/sponge.png)

3. 海绵上滴水浸透，放在手机屏幕上“再来一次”的位置。杜邦线的另一头可以连接树莓拍或Arduino的地线。

## 关于树莓派 ##

1. 打开 servo_control.py，这里需要根据实际安装位置调整舵机高点和低点位置（范围： 2.5~12.5）

2. 需要注释掉这句，这是Arduino使用的
	`#from servo_control_arduino import arduino_servo_run`
 
3. main()函数里面选择 send_time()

4. 设置树莓派的ip地址

	`ip_addr = '192.168.199.181'`

## 关于Arduino ##

 1. 因为pyfrimata库不支持Arduino Nano，请选择Arduino UNO或Arduino Mega。并根据Arduino的型号使用下列语句。
```
board = pyfirmata.Arduino(serial_int)

board = pyfirmata.ArduinoMega(serial_int)
```

 2. 烧入预置的StandardFirmata程序。

 3. 如果运行之后舵机动作缓慢或者一直发出滋滋的声音，是因为电脑USB接口供电不足所致。

## 关于 Windows ##
 1. 下载[Airplayer](https://pro.itools.cn/airplayer "Airplayer")（免安装，暂无捆绑)

 2. 配置Airplayer，画质什么的统统调到最高。启动iPhone上的Airplay，然后可以在电脑上到iPhone画面，游戏运行时需要Airplayer全屏显示。

 3. 由于Airplay传输画面时会压缩，获取的游戏画面会有颜色偏差。我修改了原算法的一些参数，增大了一些颜色上的宽容度，在我的测试中达到一个比较好的准确率。

 4. 本方案使用Pillow库截屏，截屏的尺寸为610*1080
```
im = ImageGrab.grab((654, 0, 1264, 1080)） 

im.save('a.png', 'png')
```
 
# 存在问题 #

- 采用新版算法后，计算上的误差已经很小，可以查看screenshot_backups/文件夹，看是否得到正确的计算结果。但是仍然无法一直连续击中中心，这是由于舵机的物理误差引起的，需要调节好时间系数，舵机的高点和低点。如果采用海绵+水的接触方案，注意接触面的高度会因为水的蒸发而改变。

- 舵机的摆动角度和时间系数没有绝对的数值，需要慢慢尝试，当前使用的时间系数是2.43。