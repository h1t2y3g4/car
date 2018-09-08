from classes import *
from functions import *
import pygame


def main():
    # 初始化pygame，后面不用键盘控制后可以删掉
    pygame.init()
    surface = pygame.display.set_mode([250, 250])
    surface.fill((0, 0, 0))
    pygame.display.set_caption("control")

    # 初始化全局变量
    setting = Settings()
    status = Status()

    # 初始化IO口
    GPIO_init()

    # 初始化帧数
    fps = pygame.time.Clock()
    pygame.display.flip()

    # 开始操控主循环
    while True:
        find_way(setting, status)

        # 检查事件函数中修改status中的属性
        check_event(status)

        # 对status中关于车辆移动的属性作出反应
        move(setting, status)
        # 是否需要转动舵机
        steering_engine(setting, status)
        # 测距
        find_distance(setting, status)
        # 测试颜色
        find_color(setting, status)

        pygame.display.flip()


if __name__ == '__main__':
    main()

