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
    d1.start(0)
    d2.start(0)
    while True:
        check_event(status)
        response_event(setting, status, d1, d2)


class Settings:

    def __init__(self):
        self.f_1 = 19
        self.f_2 = 26
        self.d_1 = 6
        self.d_2 = 13

        self.sleep_time = 0.3
        self.duty_cycle = 90


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


def response_event(setting, status, d1, d2):
    if status.forward_flag:
        GPIO.output(setting.f_1, GPIO.HIGH)
        GPIO.output(setting.f_2, GPIO.LOW)
        if status.back_off_flag:
            GPIO.output(setting.f_1, GPIO.LOW)
            GPIO.output(setting.f_2, GPIO.LOW)
        else:
            if status.left_turn_flag and status.right_turn_flag:
                d1.ChangeDutyCycle(0)
                d2.ChangeDutyCycle(0)
            else:
                if status.left_turn_flag:
                    d1.ChangeDutyCycle(setting.duty_cycle)
                    d2.ChangeDutyCycle(0)
                elif status.right_turn_flag:
                    d1.ChangeDutyCycle(0)
                    d2.ChangeDutyCycle(setting.duty_cycle)
                else:
                    if status.down_time1 - status.up_time2 <= setting.sleep_time:
                        time.sleep(setting.sleep_time - (status.down_time1 - status.up_time2))
                    d1.ChangeDutyCycle(0)
                    d2.ChangeDutyCycle(0)
    else:
        GPIO.output(setting.f_1, GPIO.LOW)
        GPIO.output(setting.f_2, GPIO.LOW)
        if status.back_off_flag:
            GPIO.output(setting.f_1, GPIO.LOW)
            GPIO.output(setting.f_2, GPIO.HIGH)
            if status.left_turn_flag and status.right_turn_flag:
                d1.ChangeDutyCycle(0)
                d2.ChangeDutyCycle(0)
            else:
                if status.left_turn_flag:
                    d1.ChangeDutyCycle(setting.duty_cycle)
                    d2.ChangeDutyCycle(0)
                elif status.right_turn_flag:
                    d1.ChangeDutyCycle(0)
                    d2.ChangeDutyCycle(setting.duty_cycle)
                else:
                    if status.down_time2 - status.up_time1 <= setting.sleep_time:
                        time.sleep(setting.sleep_time - (status.down_time2 - status.up_time1))
                    d1.ChangeDutyCycle(0)
                    d2.ChangeDutyCycle(0)
        else:
            d1.ChangeDutyCycle(0)
            d2.ChangeDutyCycle(0)
            GPIO.output(setting.f_1, GPIO.LOW)
            GPIO.output(setting.f_2, GPIO.LOW)


if __name__ == '__main__':
    main()

