import multiprocessing
from soundcard.mediafoundation import SoundcardRuntimeWarning
from Trigger import SoftKbMouseV2, SoftKbMouseV3, HardKbMouse, DodgingTrigger

import warnings
warnings.filterwarnings('ignore', category=SoundcardRuntimeWarning)


SAMPLE_PATH = "./特征波形_完整.wav"

THRESHOLD = 0.1  # 阈值
EXPANSION_RATIO = 1.0  # 最大NCC系数
IS_ALLOW_SUCCESSIVE_TRIGGER = False
ACTION = 'push_space'  # 空格或双闪


if __name__ == "__main__":
    multiprocessing.freeze_support()

    kbm = SoftKbMouseV3()  # 软模拟

    action = eval("kbm.{}".format(ACTION))

    et = DodgingTrigger(SAMPLE_PATH, action, threshold=THRESHOLD, ratio=EXPANSION_RATIO,
                        is_monitor=True,
                        is_allowed_succe_dodge=IS_ALLOW_SUCCESSIVE_TRIGGER)
    et.online_listening()



