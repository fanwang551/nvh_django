CRUISE_RADAR_POINTS = {
    'front_right': [1, 5, 7, 9, 11, 13],
    'rear_left': [2, 6, 8, 10, 12, 14],
}

ACCELERATION_POINT_CANDIDATES = {
    # 数据需求文档存在测点编号差异，按优先级提供多个候选ID以兼容不同库
    'front_right': [20, 1],
    'rear_left': [21, 2],
}

AIR_CONDITION_POINTS = {
    'front_right': [17, 18, 19, 20, 21, 22, 23, 24, 25],
    'rear_left': [26, 27, 28, 29, 30, 31, 32, 33, 34],
}

SPEECH_CLARITY_POINTS = {
    'speed_100': 11,
    'speed_120': 13,
}

SUSPENSION_FRONT_POINT_CANDIDATES = [
    '左前减振器',
    '右前减振器',
    '前减振器',
]

SUSPENSION_REAR_POINT_CANDIDATES = [
    '左后减振器',
    '右后减振器',
    '后减振器',
]

SUSPENSION_MEASURE_POINTS = SUSPENSION_FRONT_POINT_CANDIDATES + SUSPENSION_REAR_POINT_CANDIDATES

SOUND_INSULATION_FREQ_FIELDS = [
    400, 500, 630, 800, 1000, 1250, 1600, 2000, 2500, 3150, 4000, 5000, 6300, 8000, 10000,
]
