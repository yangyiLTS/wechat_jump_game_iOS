# coding: utf-8
import os
import shutil
import time
import math
from PIL import Image, ImageDraw, ImageGrab
import random
import json
import socket


# === 思路 ===
# 核心：每次落稳之后截图，根据截图算出棋子的坐标和下一个块顶面的中点坐标，
#      根据两个点的距离乘以一个时间系数获得长按的时间
# 识别棋子：靠棋子的颜色来识别位置，通过截图发现最下面一行大概是一条直线，就从上往下一行一行遍历，
#         比较颜色（颜色用了一个区间来比较）找到最下面的那一行的所有点，然后求个中点，
#         求好之后再让 Y 轴坐标减小棋子底盘的一半高度从而得到中心点的坐标
# 识别棋盘：靠底色和方块的色差来做，从分数之下的位置开始，一行一行扫描，由于圆形的块最顶上是一条线，
#          方形的上面大概是一个点，所以就用类似识别棋子的做法多识别了几个点求中点，
#          这时候得到了块中点的 X 轴坐标，这时候假设现在棋子在当前块的中心，
#          根据一个通过截图获取的固定的角度来推出中点的 Y 坐标
# 最后：根据两点的坐标算距离乘以系数来获取长按时间（似乎可以直接用 X 轴距离）


# Magic Number，不设置可能无法正常执行，请根据具体截图从上到下按需设置
under_game_score_y = 170  # 截图中刚好低于分数显示区域的 Y 坐标，300 是 1920x1080 的值，2K 屏、全面屏请根据实际情况修改
press_coefficient = 2.43 # 长按的时间系数，请自己根据实际情况调节
piece_base_height_1_2 = 10  # 二分之一的棋子底座高度，可能要调节
piece_body_width = 46  # 棋子的宽度，比截图中量到的稍微大一点比较安全，可能要调节

ip_addr = '192.168.199.181' # ip地址设置

screenshot_backup_dir = 'screenshot_backups/'
if not os.path.isdir(screenshot_backup_dir):
    os.mkdir(screenshot_backup_dir)

# 使用PIL库截取Windows屏幕
def pull_screenshot():
    im = ImageGrab.grab((654, 0, 1264, 1080))
    im.save('a.png', 'png')


def send_time(time):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip_addr, 9999))
    s.send(str(time).encode('utf-8'))
    s.close()


def backup_screenshot(ts):
    # 为了方便失败的时候 debug
    if not os.path.isdir(screenshot_backup_dir):
        os.mkdir(screenshot_backup_dir)
    shutil.copy('a.png', '{}{}.png'.format(screenshot_backup_dir, ts))


def save_debug_creenshot(ts, im, piece_x, piece_y, board_x, board_y):
    draw = ImageDraw.Draw(im)
    draw.line((piece_x, piece_y) + (board_x, board_y), fill=2, width=2)
    del draw
    im.save("{}{}_d.png".format(screenshot_backup_dir, ts))


def set_button_position(im):
    # 将swipe设置为 `再来一局` 按钮的位置
    global swipe_x1, swipe_y1, swipe_x2, swipe_y2
    w, h = im.size
    left = w / 2
    top = 1003 * (h / 1280.0) + 10
    swipe_x1, swipe_y1, swipe_x2, swipe_y2 = left, top, left, top


# def jump(distance):
#     press_time = distance * press_coefficient
#     press_time = max(press_time, 200)  # 设置 200 ms 是最小的按压时间
#     press_time = int(press_time)
#     cmd = 'adb shell input swipe {} {} {} {} {}'.format(swipe_x1, swipe_y1, swipe_x2, swipe_y2, press_time)
#     print(cmd)
#     os.system(cmd)


def find_piece_and_board(im):
    w, h = im.size

    piece_x_sum = 0
    piece_x_c = 0
    piece_y_max = 0
    board_x = 0
    board_y = 0
    scan_x_border = int(w / 8)  # 扫描棋子时的左右边界
    scan_start_y = 0  # 扫描的起始y坐标
    im_pixel = im.load()
    # 以25px步长，尝试探测scan_start_y
    for i in range(under_game_score_y+25, h, 25):
        last_pixel = im_pixel[1, i]
        for j in range(1, w):
            pixel = im_pixel[j, i]
            # 不是纯色的线，则记录scan_start_y的值，准备跳出循环
            if abs(pixel[0] - last_pixel[0]) > 3 or abs(pixel[1] - last_pixel[1]) > 3 or abs(
                            pixel[2] != last_pixel[2]) > 3:
                scan_start_y = i - 25
                break
        if scan_start_y:
            break
    print("scan_start_y: ", scan_start_y)

    # 从scan_start_y开始往下扫描，棋子应位于屏幕上半部分，这里暂定不超过2/3
    for i in range(scan_start_y, int(h * 2 / 3)):
        for j in range(scan_x_border, w - scan_x_border):  # 横坐标方面也减少了一部分扫描开销
            pixel = im_pixel[j, i]
            # 根据棋子的最低行的颜色判断，找最后一行那些点的平均值，这个颜色这样应该 OK，暂时不提出来
            if (47 < pixel[0] < 60) and (45 < pixel[1] < 60) and (97 < pixel[2] < 110):
                piece_x_sum += j
                piece_x_c += 1
                piece_y_max = max(i, piece_y_max)

    if not all((piece_x_sum, piece_x_c)):
        return 0, 0, 0, 0
    piece_x = piece_x_sum / piece_x_c
    piece_y = piece_y_max - piece_base_height_1_2  # 上移棋子底盘高度的一半

    for i in range(scan_start_y, h):
        last_pixel = im_pixel[1, i]
        if board_x or board_y:
            break
        board_x_sum = 0
        board_x_c = 0

        for j in range(1, w):
            pixel = im_pixel[j, i]
            # 修掉脑袋比下一个小格子还高的情况的 bug
            if abs(j - piece_x) < piece_body_width:
                continue

            # 修掉圆顶的时候一条线导致的小 bug，这个颜色判断应该 OK，暂时不提出来
            if abs(pixel[0] - last_pixel[0]) + abs(pixel[1] - last_pixel[1]) + abs(pixel[2] - last_pixel[2]) > 20:
                board_x_sum += j
                board_x_c += 1
        if board_x_sum:
            board_x = board_x_sum / board_x_c

    # 按实际的角度来算，找到接近下一个 board 中心的坐标
    # board_y = piece_y - abs(board_x - piece_x) * abs(sample_board_y1 - sample_board_y2) / abs(sample_board_x1 - sample_board_x2)

    board_y = piece_y - abs(board_x - piece_x) * math.sqrt(3) / 3

    if not all((board_x, board_y)):
        return 0, 0, 0, 0

    return piece_x, piece_y, board_x, board_y


def main():
    while 1:
        pull_screenshot()
        filename = 'a.png'
        im = Image.open(filename)
        piece_x, piece_y, board_x, board_y = find_piece_and_board(im)
        distance = math.sqrt((board_x - piece_x) ** 2 + (board_y - piece_y) ** 2)
        t = max(press_coefficient * distance, 200)
        print("distance:  %f\npress_time:  %d\n" % (distance, t))
        ts = int(time.time())
        save_debug_creenshot(ts, im, piece_x, piece_y, board_x, board_y)
        backup_screenshot(ts)
        send_time(t)
        # 跳跃后的延时 刚好可以吃到加分
        time.sleep(2.7)




if __name__ == '__main__':
    main()