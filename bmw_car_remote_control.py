import pygame
import RPi.GPIO as GPIO
import sys
import time


def main():
    pygame.init()
    surface = pygame.display.set_mode([250, 250])
    surface.fill((0, 0, 0))
    pygame.display.set_caption("control")
    setting = Settings()
    status = Status()
    GPIO_init()
    d1 = GPIO.PWM(setting.d_1, 10000)
    d2 = GPIO.PWM(setting.d_2, 10000)
    f1 = GPIO.PWM(setting.f_1, 10000)
    f2 = GPIO.PWM(setting.f_2, 10000)
    f1.start(0)
    f2.start(0)
    d1.start(0)
    d2.start(0)
    while True:
        check_event(status)
        response_event(setting, status, d1, d2, f1, f2)


class Settings:

    def __init__(self):
        self.f_1 = 6
        self.f_2 = 13
        self.d_1 = 19
        self.d_2 = 26

        self.sleep_time = 0.3
        self.der_sleep_time = 0.02
        self.d_duty_cycle = 100
        self.f_duty_cycle = 80


class Status:

    def __init__(self):
        self.forward_flag = False
        self.left_turn_flag = False
        self.right_turn_flag = False
        self.back_off_flag = False

        self.down_time1 = time.time()
        self.up_time1 = time.time()
        self.down_time2 = time.time()
        self.up_time2 = time.time()


def GPIO_init():
    GPIO.setmode(GPIO.BCM)
    for i in (6, 13, 19, 26):
        GPIO.setup(i, GPIO.OUT, initial=GPIO.LOW)


def check_event(status):
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
            else:
                pass


def slow_speed_up(setting, status, speed_io, zero_io, turn_flag=False):
    """
    匀加速，以免过载
    :param turn_flag:
    :param setting:
    :param status:
    :param speed_io:
    :param zero_io:
    :return:
    """
    i = 0
    while status.down_time1 - status.up_time2 <= setting.sleep_time:
        i += int(setting.f_duty_cycle / (setting.sleep_time / setting.der_sleep_time))
        if turn_flag:
            if i > int(setting.f_duty_cycle/2):
                break
        else:
            if i > setting.f_duty_cycle:
                break
        speed_io.ChangeDutyCycle(i)
        zero_io.ChangeDutyCycle(0)
        time.sleep(setting.der_sleep_time)


def response_event(setting, status, d1, d2, f1, f2):
    if status.forward_flag:
        if status.back_off_flag:
            f1.ChangeDutyCycle(0)
            f2.ChangeDutyCycle(0)
        else:
            if status.left_turn_flag and status.right_turn_flag:
                slow_speed_up(setting, status, f1, f2)
                f1.ChangeDutyCycle(setting.f_duty_cycle)
                f2.ChangeDutyCycle(0)
                d1.ChangeDutyCycle(0)
                d2.ChangeDutyCycle(0)
            else:
                if status.left_turn_flag:
                    slow_speed_up(setting, status, f1, f2, True)
                    f1.ChangeDutyCycle(int(setting.f_duty_cycle/2))
                    f2.ChangeDutyCycle(0)
                    d1.ChangeDutyCycle(setting.d_duty_cycle)
                    d2.ChangeDutyCycle(0)
                elif status.right_turn_flag:
                    slow_speed_up(setting, status, f1, f2, True)
                    f1.ChangeDutyCycle(int(setting.f_duty_cycle/2))
                    f2.ChangeDutyCycle(0)
                    d1.ChangeDutyCycle(0)
                    d2.ChangeDutyCycle(setting.d_duty_cycle)
                else:
                    if status.down_time1 - status.up_time2 <= setting.sleep_time:
                        time.sleep(setting.sleep_time - (status.down_time1 - status.up_time2))
                    slow_speed_up(setting, status, f1, f2)
                    f1.ChangeDutyCycle(setting.f_duty_cycle)
                    f2.ChangeDutyCycle(0)
                    d1.ChangeDutyCycle(0)
                    d2.ChangeDutyCycle(0)
    else:
        f1.ChangeDutyCycle(0)
        f2.ChangeDutyCycle(0)
        if status.back_off_flag:
            if status.left_turn_flag and status.right_turn_flag:
                slow_speed_up(setting, status, f2, f1)
                f1.ChangeDutyCycle(0)
                f2.ChangeDutyCycle(setting.f_duty_cycle)
                d1.ChangeDutyCycle(0)
                d2.ChangeDutyCycle(0)
            else:
                if status.left_turn_flag:
                    slow_speed_up(setting, status, f2, f1, True)
                    f1.ChangeDutyCycle(0)
                    f2.ChangeDutyCycle(int(setting.f_duty_cycle/2))
                    d1.ChangeDutyCycle(setting.d_duty_cycle)
                    d2.ChangeDutyCycle(0)
                elif status.right_turn_flag:
                    slow_speed_up(setting, status, f2, f1, True)
                    f1.ChangeDutyCycle(0)
                    f2.ChangeDutyCycle(int(setting.f_duty_cycle / 2))
                    d1.ChangeDutyCycle(0)
                    d2.ChangeDutyCycle(setting.d_duty_cycle)
                else:
                    if status.down_time2 - status.up_time1 <= setting.sleep_time:
                        time.sleep(setting.sleep_time - (status.down_time2 - status.up_time1))
                    slow_speed_up(setting, status, f2, f1)
                    f1.ChangeDutyCycle(0)
                    f2.ChangeDutyCycle(setting.f_duty_cycle)
                    d1.ChangeDutyCycle(0)
                    d2.ChangeDutyCycle(0)

        else:
            d1.ChangeDutyCycle(0)
            d2.ChangeDutyCycle(0)
            f1.ChangeDutyCycle(0)
            f2.ChangeDutyCycle(0)


if __name__ == '__main__':
    main()

