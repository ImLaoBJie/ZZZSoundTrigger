from soundcard.mediafoundation import SoundcardRuntimeWarning
from Trigger import SoftKbMouse, HardKbMouse, DodgingTrigger

import warnings
warnings.filterwarnings('ignore', category=SoundcardRuntimeWarning)


SAMPLE_PATH = "./游戏内样本_完整3.wav"

COM_NAME = 'COM3'


if __name__ == "__main__":
    kbm = SoftKbMouse()  # 软模拟
    # kbm = HardKbMouse(COM_NAME)  # 硬模拟

    et = DodgingTrigger(SAMPLE_PATH, kbm, is_monitor=True)
    et.online_listening()



