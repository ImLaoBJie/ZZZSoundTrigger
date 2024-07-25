import multiprocessing
from soundcard.mediafoundation import SoundcardRuntimeWarning
from Trigger import SoftKbMouseV2, HardKbMouse, DodgingTrigger

import warnings
warnings.filterwarnings('ignore', category=SoundcardRuntimeWarning)


SAMPLE_PATH = "./特征波形_完整.wav"

COM_NAME = 'COM3'

THRESHOLD = 0.1  # 阈值
EXPANSION_RATIO = 1.0  # 最大NCC系数


if __name__ == "__main__":
    multiprocessing.freeze_support()

    kbm = SoftKbMouseV2()  # 软模拟
    # kbm = HardKbMouse(COM_NAME)  # 硬模拟

    action = kbm.push_space

    et = DodgingTrigger(SAMPLE_PATH, action, threshold=THRESHOLD, ratio=EXPANSION_RATIO, is_monitor=True)
    et.online_listening()



