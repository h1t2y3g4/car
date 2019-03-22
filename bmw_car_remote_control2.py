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
		self.f_1 = 17
		self.f_2 = 27
		self.d_1 = 22
		self.d_2 = 23

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
	for i in (17, 27, 22, 23):
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


def response_event(setting, status):
	if status.forward_flag:
		if status.back_off_flag:
			GPIO.output(setting.d_1, GPIO.LOW)
			GPIO.output(setting.d_2, GPIO.LOW)
			GPIO.output(setting.f_1, GPIO.LOW)
			GPIO.output(setting.f_2, GPIO.LOW)
		else:
			if status.left_turn_flag and status.right_turn_flag:
				GPIO.output(setting.d_1, GPIO.HIGH)
				GPIO.output(setting.d_2, GPIO.LOW)
				GPIO.output(setting.f_1, GPIO.LOW)
				GPIO.output(setting.f_2, GPIO.LOW)
			else:
				if status.left_turn_flag:
					GPIO.output(setting.d_1, GPIO.HIGH)
					GPIO.output(setting.d_2, GPIO.LOW)
					GPIO.output(setting.f_1, GPIO.HIGH)
					GPIO.output(setting.f_2, GPIO.LOW)
				elif status.right_turn_flag:
					GPIO.output(setting.d_1, GPIO.HIGH)
					GPIO.output(setting.d_2, GPIO.LOW)
					GPIO.output(setting.f_1, GPIO.LOW)
					GPIO.output(setting.f_2, GPIO.HIGH)
				else:
					if status.down_time1 - status.up_time2 <= setting.sleep_time:
						time.sleep(setting.sleep_time - (status.down_time1 - status.up_time2))
						GPIO.output(setting.d_1, GPIO.HIGH)
						GPIO.output(setting.d_2, GPIO.LOW)
						GPIO.output(setting.f_1, GPIO.LOW)
						GPIO.output(setting.f_2, GPIO.LOW)
	else:
		if status.back_off_flag:
			if status.left_turn_flag and status.right_turn_flag:
				GPIO.output(setting.d_1, GPIO.LOW)
				GPIO.output(setting.d_2, GPIO.HIGH)
				GPIO.output(setting.f_1, GPIO.LOW)
				GPIO.output(setting.f_2, GPIO.LOW)
			else:
				if status.left_turn_flag:
					GPIO.output(setting.d_1, GPIO.LOW)
					GPIO.output(setting.d_2, GPIO.HIGH)
					GPIO.output(setting.f_1, GPIO.HIGH)
					GPIO.output(setting.f_2, GPIO.LOW)
				elif status.right_turn_flag:
					GPIO.output(setting.d_1, GPIO.LOW)
					GPIO.output(setting.d_2, GPIO.HIGH)
					GPIO.output(setting.f_1, GPIO.LOW)
					GPIO.output(setting.f_2, GPIO.HIGH)
				else:
					if status.down_time2 - status.up_time1 <= setting.sleep_time:
						time.sleep(setting.sleep_time - (status.down_time2 - status.up_time1))
					GPIO.output(setting.d_1, GPIO.LOW)
					GPIO.output(setting.d_2, GPIO.HIGH)
					GPIO.output(setting.f_1, GPIO.LOW)
					GPIO.output(setting.f_2, GPIO.LOW)

		else:
			GPIO.output(setting.d_1, GPIO.LOW)
			GPIO.output(setting.d_2, GPIO.LOW)
			GPIO.output(setting.f_1, GPIO.LOW)
			GPIO.output(setting.f_2, GPIO.LOW)


if __name__ == '__main__':
	main()

