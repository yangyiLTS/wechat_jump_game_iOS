#  -*- coding: utf-8 -*-
import cv2
import numpy as np
import os
import shutil
import time
import math
from PIL import Image, ImageDraw, ImageGrab
import socket

# =================================
#   使用Arduino需要取消下面一句的注释
#
#from servo_control_arduino import arduino_servo_run
#
#
# =================================


# =================================
#  使用树莓派需要设置ip地址
#
ip_addr = '192.168.199.181'
#
#
# ================================

# Magic Number，不设置可能无法正常执行，请根据具体截图从上到下按需设置
under_game_score_y = 170  # 截图中刚好低于分数显示区域的 Y 坐标
press_coefficient = 2.39 # 长按的时间系数，
piece_base_height_1_2 = 10  # 二分之一的棋子底座高度，可能要调节

w,h = 610,1080

special_board = ['music_player.png','cesspool.png'] # 有加分的目标
piece_template = cv2.imread('piece.png',0) # 棋子模板
white_point_template = cv2.imread('white_point.png',0) # 白点模板

piece_w, piece_h = piece_template.shape[::-1]

screenshot_backup_dir = 'screenshot_backups/'
screenshot_backup_dir2 = 'train_data/'
if not os.path.isdir(screenshot_backup_dir):
    os.mkdir(screenshot_backup_dir)

method = 'cv2.TM_CCORR_NORMED'
meth = eval('cv2.TM_CCORR_NORMED')






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

def backup_screenshot2(filename,ts):
    # 为了方便失败的时候 debug
    if not os.path.isdir(screenshot_backup_dir):
        os.mkdir(screenshot_backup_dir)
    shutil.copy(filename, '{}{}.png'.format(screenshot_backup_dir, ts))


def save_debug_creenshot(ts, im, piece_x, piece_y, board_x, board_y):
    draw = ImageDraw.Draw(im)
    draw.line((piece_x, piece_y) + (board_x, board_y), fill=2, width=2)
    del draw
    im.save("{}{}_d.png".format(screenshot_backup_dir, ts))

# 模板匹配 获取棋子坐标
def find_piece(img):
    res = cv2.matchTemplate(img, piece_template, meth)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    piece_x, piece_y = max_loc
    piece_x = int(piece_x + piece_w / 2)
    piece_y = piece_y + piece_h - piece_base_height_1_2
    return piece_x, piece_y

def find_board(img,piece_x,piece_y):

    board_x = 0
    board_y = 0
    result = 0
    img2 = img.copy()
    method = 'cv2.TM_CCOEFF_NORMED'
    img[:170,] = 0

    for i in special_board:
        template = cv2.imread(i, 0)
        template_w, template_h = template.shape[::-1]
        res = cv2.matchTemplate(img, template, meth)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        if max_val > 0.99 and (max_loc[1] + template_h / 2) < piece_y:
            board_x = max_loc[0] + template_w / 2
            board_y = max_loc[1] + template_h / 2
            result = 2
            print('found special_board  max_val:  %f' % max_val)
            return board_x, board_y, result

    img2 = cv2.GaussianBlur(img2, (3, 3), 0)
    img_canny = cv2.Canny(img2, 1, 10)

    # res = cv2.matchTemplate(img_canny, white_point_template, eval(method))
    # min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    # if max_val > 0.9:
    #     board_x = max_loc[0] + 22
    #     board_y = max_loc[1] + 22
    #     result = 1
    #     print('white_point_val:  %f' % max_val)
    #     return board_x, board_y, result

    for i in range(piece_y - 120, piece_y + 10):
        for j in range(piece_x - 22, piece_x + 22):
            img_canny[i][j] = 0

    img_canny[:,:2] = 0
    board_y_top = under_game_score_y

    # cv2.imwrite('c2.png',img_canny)
    for i in img_canny[under_game_score_y:]:
        # i是一整行像素的list，max返回最大值，一旦最大值存在，则找到了board_y_top
        if max(i):
            break
        board_y_top += 1

    board_x = int(np.mean(np.nonzero(img_canny[board_y_top])))
    board_y_bottom = board_y_top + 10


    board_y = board_y_top

    x1 = board_x
    fail_count = 0
    if board_x > piece_x:
        for i in img_canny[board_y_top:board_y_top+80]:
            try:
                x = max(np.nonzero(i)[0])
            except:
                pass
            if x > x1:
                x1 = x
                board_y += 1
                if fail_count < 5 and fail_count != 0:
                    fail_count -= 1
            elif fail_count > 6 and board_y - board_y_bottom >10:
                result = 1
                board_y -= 1
                break
            elif fail_count > 6 and board_y - board_y_bottom <= 10:
                result = 0
                break

            else:
                fail_count += 1

    else:
        for i in img_canny[board_y_top:board_y_top+80]:
            try:
                x = min(np.nonzero(i)[0])
            except:
                pass
            if  x < x1:
                x1 = x
                board_y += 1
                if fail_count < 5 and fail_count != 0:
                    fail_count -= 1
            elif fail_count > 6 and board_y - board_y_bottom > 10:
                board_y -= 1
                result = 1
                break
            elif fail_count > 6 and board_y - board_y_bottom <= 10:
                result = 0
                break
            else:
                fail_count += 1

    if result == 0:
        board_y = piece_y - abs(board_x - piece_x) * math.sqrt(3) / 3
        result = 1
        # print("return by old")


    # print('result:  %d' % result)
    return board_x, board_y, result



def main():
    while True:
        pull_screenshot()
        filename = 'a.png'
        img = cv2.imread(filename,0)
        img2 = Image.open(filename)

        piece_x , piece_y = find_piece(img)
        board_x, board_y, result = find_board(img, piece_x, piece_y)

        distance = math.sqrt((board_x - piece_x) ** 2 + (board_y - piece_y) ** 2)
        t = max(press_coefficient * distance, 200)
        print("distance:  %f\npress_time:  %d\n" % (distance, t))

        ts = int(time.time())
        save_debug_creenshot(ts, img2, piece_x, piece_y, board_x, board_y)
        backup_screenshot2(filename, ts)

        # send_time() 为树莓派控制函数
        send_time(t)

        # arduino_servo_run () 为arduino控制函数
        ##arduino_servo_run(t/1000)


        time.sleep(2 + result)





if __name__ == '__main__':
    main()
