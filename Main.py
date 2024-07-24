import multiprocessing
from soundcard.mediafoundation import SoundcardRuntimeWarning
from Trigger import SoftKbMouseV2, HardKbMouse, DodgingTrigger

import warnings
warnings.filterwarnings('ignore', category=SoundcardRuntimeWarning)


SAMPLE_PATH = "./特征波形_完整.wav"

COM_NAME = 'COM3'


if __name__ == "__main__":
    multiprocessing.freeze_support()

    kbm = SoftKbMouseV2()  # 软模拟
    # kbm = HardKbMouse(COM_NAME)  # 硬模拟

    et = DodgingTrigger(SAMPLE_PATH, kbm, is_monitor=True)
    et.online_listening()



