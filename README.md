感谢来自 [wangshub](https://github.com/wangshub "wangshub") 的跳跃距离算法

原项目地址：[wangshub/wechat_jump_game](https://github.com/wangshub/wechat_jump_game "https://github.com/wangshub/wechat_jump_game")

知乎专栏：[教你用Python来玩微信跳一跳](https://zhuanlan.zhihu.com/p/32452473 "教你用Python来玩微信跳一跳")

----------

本项目知乎专栏：[python玩“跳一跳” iOS+Win版](https://zhuanlan.zhihu.com/p/32526110 "python玩“跳一跳” iOS+Win版")

目前已有的iOS跳一跳辅助需要macOS环境下的WebDriverAgentRunner。而现在介绍的方法在Windows环境下通过物理方法实现，不需要macOS也不需要越狱。


# 运行环境&工具 #


- Python 3.6 in Windows
- Python PIL库
- 局域网环境
- iToools Airplayer
- 树莓派 或 arduino （本文使用树莓派）
- SG90 舵机
- 杜邦线、纸板
- 一小块海绵
- 橙子或其它多汁水果（可选）


# 基本思路 #

1. 使用iOS自带Airplay服务将游戏画面投影到电脑上

2. 使用PIL库截取电脑屏幕，获得游戏画面

3. 分析图片，计算出跳跃距离，乘以时间系数获得按压时间

4. 将按压时间发送至树莓派，树莓派控制舵机点击手机屏幕


# 原理 & 步骤 #

## 舵机 & 控制器 部分 ##

1.树莓派（OS：Raspbian Jessie）连接上局域网，下载 servo_control.py到树莓派；

2.拿一根杜邦线粘在舵机的摆臂上，并且固定好舵机。如图：

![](https://github.com/yangyiLTS/wechat_jump_game_iOS/raw/master/data/servo.jpg)

3.取一小块海绵，约10mm\*10mm\*5mm，不必太精确。海绵中间挖一个小洞。大概是这样：
![](https://github.com/yangyiLTS/wechat_jump_game_iOS/raw/master/data/sponge.png)

4.海绵上滴水浸透，放在手机屏幕上“再来一次”的位置。杜邦线的另一头插进橙子（触发电容屏需要在屏幕上形成一个电场，我尝试过连接干电池负极的方案，但是效果不理想，最后不得已拿了室友的一个橙子。当然一直捏着或者含着导线也是可以的）。

5.舵机连接上树莓派，电源使用5v，舵机控制线接在GPIO18，
如图

6.需要根据实际安装位置调整舵机高点和低点位置`servo_down = 3.8
servo_up = 5`（范围： 2.5~12.5）

7.最终效果
![](https://github.com/yangyiLTS/wechat_jump_game_iOS/raw/master/data/final.png)

## Windows 部分 ##
1. 下载[Airplayer](https://pro.itools.cn/airplayer "Airplayer")（免安装，暂无捆绑)

2. 配置Airplayer，画质什么的统统调到最高。启动iPhone上的Airplay，然后可以在电脑上到iPhone画面，游戏运行时需要Airplayer全屏显示。
	
3. 安装PIL库
	本文使用PIL库的ImageGrab截屏
	
	`im = ImageGrab.grab((654, 0, 1264, 1080))
     im.save('a.png', 'png')`

	其中`(654, 0, 1264, 1080)`是截屏的范围，我的显示器分辨率是1080p，截取屏幕中间的部分得到的图片大小是610*1080，但这个时候图片最左边的一列的像素是黑色的。

4.下载`wechat_jump_auto_iOS_Win.py`，我的显示器分辨率是1920*1080，手机是iPhone 7。如果使用不同的设备需要更改时间系数等参数。此外，由于Airplay传输画面时会压缩，获取的游戏画面会有颜色偏差。我修改了原算法的一些参数，增大了一些颜色上的宽容度，在我的测试中达到一个比较好的准确率。

# 运行 #

1. 打开游戏画面，Airplayer窗口全屏

2. 树莓派上运行`servo_control.py`

3. Windows运行`wechat_jump_auto_iOS_Win.py`


# 存在问题 #

- 由于是物理点击屏幕，会产生一定的操作误差。操作误差由时间常数误差、舵机运动时间、杜邦线触点插进海绵的深度等等因素引起。而当前使用的算法在一种情况下会出现误差叠加的问题。

- 舵机的摆动角度和时间系数没有绝对的数值，需要慢慢尝试，当前使用的时间系数是2.43。