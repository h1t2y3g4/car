import pygame
import RPi.GPIO as GPIO
import sys
import time
import math


def GPIO_init():
    """
    初始化io口
    :return:
    """
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    for i in (21, 20, 16, 12, 6, 13, 19, 26, 7, 5):
        GPIO.setup(i, GPIO.OUT, initial=GPIO.LOW)
    for i in (8, 25, 24, 23, 11, 9):
        GPIO.setup(i, GPIO.IN)


def check_event(status):
    """
    修改status中的属性，操控后续函数动作
    :param status:
    :return:
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE):
            GPIO.cleanup()
            pygame.quit()
            sys.exit()
        else:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    status.forward_flag = True
                    status.down_time1 = time.time()
                    print("forward")
                if event.key == pygame.K_LEFT:
                    status.left_turn_flag = True
                    print("forward and left")
                if event.key == pygame.K_RIGHT:
                    status.right_turn_flag = True
                    print("forward and right")
                if event.key == pygame.K_DOWN:
                    status.back_off_flag = True
                    status.down_time2 = time.time()
                    print("back off")
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_UP:
                    status.forward_flag = False
                    status.up_time1 = time.time()
                    print("stop")
                if event.key == pygame.K_LEFT:
                    status.left_turn_flag = False
                    print("stop left")
                if event.key == pygame.K_RIGHT:
                    status.right_turn_flag = False
                    print("stop right")
                if event.key == pygame.K_DOWN:
                    status.back_off_flag = False
                    status.up_time2 = time.time()
                    print("stop back off")
                if event.key == pygame.K_z:
                    status.steering_engine_flag = True
                    status.steering_shrink_flag = True
                    print("收缩爪子")
                if event.key == pygame.K_x:
                    status.steering_engine_flag = True
                    status.steering_open_flag = True
                    print("打开爪子")
                if event.key == pygame.K_a:
                    status.find_distance_flag = True
                    print("开始测距")
            else:
                pass


def find_way_check_event():
    """
    修改status中的属性，操控后续函数动作
    :param setting:
    :param status:
    :return:
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE):
            GPIO.cleanup()
            pygame.quit()
            sys.exit()


def find_way(setting, status):
    if GPIO.input(setting.way_L1):
        L1 = True
        print("L1真")
    else:
        L1 = False
    if GPIO.input(setting.way_R1):
        R1 = True
        print("R1真")
    else:
        R1 = False
    if GPIO.input(setting.way_M1):
        M1 = True
        print("M1真")
    else:
        M1 = False
    if GPIO.input(setting.way_L2):
        L2 = True
        print("L2真")
    else:
        L2 = False
    if GPIO.input(setting.way_R2):
        R2 = True
        print("R2真")
    else:
        R2 = False
    print("----------------------------")

    if M1:
        if L2 and R2:
            status.forward_flag = True
        elif L2:
            status.right_turn_flag


# 识别颜色
def find_color(setting, status):
    pass


# 测距
def find_distance(setting, status):
    if status.find_distance_flag and status.find_distance_times < setting.protect_times:
        distances = []
        for i in range(setting.times):
            # 发出触发信号
            GPIO.output(setting.trig, GPIO.HIGH)
            # 保持10us以上（我选择15us）
            time.sleep(0.000015)
            GPIO.output(setting.trig, GPIO.LOW)
            # 设置超时保护
            protect_time1 = time.time()
            while not GPIO.input(setting.echo):
                protect_time2 = time.time()
                der_protect_time = protect_time2 - protect_time1
                if der_protect_time > setting.protect_time:
                    print("第" + str(i + 1) + "次开始时超时")
                    status.out_range_time = True
                    break
                pass
            # 发现高电平时开时计时
            t1 = time.time()
            # 设置超时保护
            protect_time1 = time.time()
            while GPIO.input(setting.echo):
                protect_time2 = time.time()
                der_protect_time = protect_time2 - protect_time1
                if der_protect_time > setting.protect_time:
                    print("第" + str(i + 1) + "次结束时超时")
                    status.out_range_time = True
                    break
                pass
            # 高电平结束停止计时
            t2 = time.time()
            # set temperature
            temperature = 15
            # 返回距离，单位为cm
            distance = ((t2 - t1) * 0.5 * 311.45 * math.sqrt(1 + temperature / 273.15)) * 100
            if not status.out_range_time:
                distances.append(distance)
            status.out_range_time = False
        if len(distances) <= 2:
            status.find_distance_times += 1
            find_distance(setting, status)
            return None
        status.distance = sum(distances)/setting.times
        print(status.distance)
        status.find_distance_flag = False


def steering_engine(setting, status):
    if status.steering_engine_flag:
        if status.steering_shrink_flag:
            for i in range(3):
                GPIO.output(setting.steering_engine, GPIO.HIGH)
                time.sleep(setting.shrink_sleep_time)
                GPIO.output(setting.steering_engine, GPIO.LOW)
                time.sleep(0.05)
            status.steering_engine_flag = False
            status.steering_shrink_flag = False
        elif status.steering_open_flag:
            for i in range(3):
                GPIO.output(setting.steering_engine, GPIO.HIGH)
                time.sleep(setting.open_sleep_time)
                GPIO.output(setting.steering_engine, GPIO.LOW)
                time.sleep(0.05)
            status.steering_engine_flag = False
            status.steering_open_flag = False


def move(setting, status):
    """
    对status中关于车辆移动的属性作出反应
    :param setting:
    :param status:
    :return:
    """
    if status.forward_flag:
        GPIO.output(setting.L1_2, GPIO.LOW)
        GPIO.output(setting.R1_2, GPIO.LOW)
        GPIO.output(setting.L2_2, GPIO.LOW)
        GPIO.output(setting.R2_2, GPIO.LOW)
        if status.back_off_flag:
            GPIO.output(setting.L1_1, GPIO.LOW)
            GPIO.output(setting.R1_1, GPIO.LOW)
            GPIO.output(setting.L2_1, GPIO.LOW)
            GPIO.output(setting.R2_1, GPIO.LOW)
        else:
            if status.left_turn_flag and status.right_turn_flag:
                GPIO.output(setting.L1_1, GPIO.HIGH)
                GPIO.output(setting.R1_1, GPIO.HIGH)
                GPIO.output(setting.L2_1, GPIO.HIGH)
                GPIO.output(setting.R2_1, GPIO.HIGH)
            else:
                if status.left_turn_flag:
                    GPIO.output(setting.L1_1, GPIO.LOW)
                    GPIO.output(setting.R1_1, GPIO.HIGH)
                    GPIO.output(setting.L2_1, GPIO.LOW)
                    GPIO.output(setting.R2_1, GPIO.HIGH)
                    GPIO.output(setting.L1_2, GPIO.HIGH)
                    GPIO.output(setting.R1_2, GPIO.LOW)
                    GPIO.output(setting.L2_2, GPIO.HIGH)
                    GPIO.output(setting.R2_2, GPIO.LOW)
                elif status.right_turn_flag:
                    GPIO.output(setting.L1_1, GPIO.HIGH)
                    GPIO.output(setting.R1_1, GPIO.LOW)
                    GPIO.output(setting.L2_1, GPIO.HIGH)
                    GPIO.output(setting.R2_1, GPIO.LOW)
                    GPIO.output(setting.L1_2, GPIO.LOW)
                    GPIO.output(setting.R1_2, GPIO.HIGH)
                    GPIO.output(setting.L2_2, GPIO.LOW)
                    GPIO.output(setting.R2_2, GPIO.HIGH)
                else:
                    if status.down_time1 - status.up_time2 <= setting.sleep_time:
                        time.sleep(setting.sleep_time - (status.down_time1 - status.up_time2))
                    GPIO.output(setting.L1_1, GPIO.HIGH)
                    GPIO.output(setting.R1_1, GPIO.HIGH)
                    GPIO.output(setting.L2_1, GPIO.HIGH)
                    GPIO.output(setting.R2_1, GPIO.HIGH)
    else:
        GPIO.output(setting.L1_1, GPIO.LOW)
        GPIO.output(setting.R1_1, GPIO.LOW)
        GPIO.output(setting.L2_1, GPIO.LOW)
        GPIO.output(setting.R2_1, GPIO.LOW)
        if status.back_off_flag:
            if status.left_turn_flag and status.right_turn_flag:
                GPIO.output(setting.L1_2, GPIO.HIGH)
                GPIO.output(setting.R1_2, GPIO.HIGH)
                GPIO.output(setting.L2_2, GPIO.HIGH)
                GPIO.output(setting.R2_2, GPIO.HIGH)
            else:
                if status.left_turn_flag:
                    GPIO.output(setting.L1_2, GPIO.LOW)
                    GPIO.output(setting.R1_2, GPIO.HIGH)
                    GPIO.output(setting.L2_2, GPIO.LOW)
                    GPIO.output(setting.R2_2, GPIO.HIGH)
                    GPIO.output(setting.L1_1, GPIO.HIGH)
                    GPIO.output(setting.R1_1, GPIO.LOW)
                    GPIO.output(setting.L2_1, GPIO.HIGH)
                    GPIO.output(setting.R2_1, GPIO.LOW)
                elif status.right_turn_flag:
                    GPIO.output(setting.L1_2, GPIO.HIGH)
                    GPIO.output(setting.R1_2, GPIO.LOW)
                    GPIO.output(setting.L2_2, GPIO.HIGH)
                    GPIO.output(setting.R2_2, GPIO.LOW)
                    GPIO.output(setting.L1_1, GPIO.LOW)
                    GPIO.output(setting.R1_1, GPIO.HIGH)
                    GPIO.output(setting.L2_1, GPIO.LOW)
                    GPIO.output(setting.R2_1, GPIO.HIGH)
                else:
                    if status.down_time2 - status.up_time1 <= setting.sleep_time:
                        time.sleep(setting.sleep_time - (status.down_time2 - status.up_time1))
                    GPIO.output(setting.L1_2, GPIO.HIGH)
                    GPIO.output(setting.R1_2, GPIO.HIGH)
                    GPIO.output(setting.L2_2, GPIO.HIGH)
                    GPIO.output(setting.R2_2, GPIO.HIGH)
        else:
            GPIO.output(setting.L1_2, GPIO.LOW)
            GPIO.output(setting.R1_2, GPIO.LOW)
            GPIO.output(setting.L2_2, GPIO.LOW)
            GPIO.output(setting.R2_2, GPIO.LOW)