import time


class Settings:

    def __init__(self):
        # 设置电机io口
        self.L1_1 = 21
        self.L1_2 = 20
        self.R1_1 = 16
        self.R1_2 = 12
        self.L2_1 = 6
        self.L2_2 = 13
        self.R2_1 = 19
        self.R2_2 = 26
        self.sleep_time = 0.3

        self.steering_engine = 7  # 舵机接口
        self.shrink_sleep_time = 0.0010  # 设置收缩时pwm中高电平时长
        self.open_sleep_time = 0.0013  # 设置收缩时pwm中低电平时长

        self.trig = 5  # 超声波模块Trig口
        self.echo = 8  # 超声波模块echo口
        self.times = 6  # 每一下超声波测距测量次数
        self.protect_time = 0.4  # 每一下测距保护时长
        self.protect_times = 2  # 超声波总共进行的大循环次数。如果超出此次数就跳出。

        # 设置循迹模块io口
        self.way_L1 = 25
        self.way_R1 = 24
        self.way_M1 = 23
        self.way_L2 = 11
        self.way_R2 = 9

        self.fps = 60  # 设置帧数


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

        self.steering_engine_flag = False  # 允许爪子动的总开关
        self.steering_shrink_flag = False  # 爪子收缩开关
        self.steering_open_flag = False  # 爪子打开开关

        self.find_distance_flag = False  # 是否进行测距的开关
        self.distance = 10  # 默认距离
        self.out_range_time = False  # 超出测距时长开关
        self.find_distance_times = 0  # 超声波测距中进行的大循环的次数
