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
    while True:
        check_event(status)
        response_event(setting, status)


class Settings:

    def __init__(self):
        self.L1_1 = 21
        self.L1_2 = 20
        self.R1_1 = 16
        self.R1_2 = 12
        self.L2_1 = 6
        self.L2_2 = 13
        self.R2_1 = 19
        self.R2_2 = 26

        self.sleep_time = 0.3


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
    for i in (21, 20, 16, 12, 6, 13, 19, 26):
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


def response_event(setting, status):
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
                elif status.right_turn_flag:
                    GPIO.output(setting.L1_1, GPIO.HIGH)
                    GPIO.output(setting.R1_1, GPIO.LOW)
                    GPIO.output(setting.L2_1, GPIO.HIGH)
                    GPIO.output(setting.R2_1, GPIO.LOW)
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
                elif status.right_turn_flag:
                    GPIO.output(setting.L1_2, GPIO.HIGH)
                    GPIO.output(setting.R1_2, GPIO.LOW)
                    GPIO.output(setting.L2_2, GPIO.HIGH)
                    GPIO.output(setting.R2_2, GPIO.LOW)
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


if __name__ == '__main__':
    main()

