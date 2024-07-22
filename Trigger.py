import time
import random

import serial

import numpy as np

import librosa

import ctypes
from ctypes import wintypes

from Listener import GameAudioListener
from Monitor import WaveMonitor

user32 = ctypes.WinDLL('user32', use_last_error=True)
INPUT_KEYBOARD = 1
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_UNICODE = 0x0004
MAPVK_VK_TO_VSC = 0


class MOUSEINPUT(ctypes.Structure):
    _fields_ = (("dx", wintypes.LONG),
                ("dy", wintypes.LONG),
                ("mouseData", wintypes.DWORD),
                ("dwFlags", wintypes.DWORD),
                ("time", wintypes.DWORD),
                ("dwExtraInfo", wintypes.WPARAM))


class KEYBDINPUT(ctypes.Structure):
    _fields_ = (("wVk", wintypes.WORD),
                ("wScan", wintypes.WORD),
                ("dwFlags", wintypes.DWORD),
                ("time", wintypes.DWORD),
                ("dwExtraInfo", wintypes.WPARAM))

    def __init__(self, *args, **kwds):
        super(KEYBDINPUT, self).__init__(*args, **kwds)
        if not self.dwFlags & KEYEVENTF_UNICODE:
            self.wScan = user32.MapVirtualKeyExW(self.wVk,
                                                 MAPVK_VK_TO_VSC, 0)


class HARDWAREINPUT(ctypes.Structure):
    _fields_ = (("uMsg", wintypes.DWORD),
                ("wParamL", wintypes.WORD),
                ("wParamH", wintypes.WORD))


class INPUT(ctypes.Structure):
    class _INPUT(ctypes.Union):
        _fields_ = (("ki", KEYBDINPUT),
                    ("mi", MOUSEINPUT),
                    ("hi", HARDWAREINPUT))

    _anonymous_ = ("_input",)
    _fields_ = (("type", wintypes.DWORD),
                ("_input", _INPUT))


class SoftKbMouse:
    PRESS_TIME = 0.1  # s

    # 系统层实现: https://stackoverflow.com/questions/54624221/simulate-physical-keypress-in-python-without-raising
    # -lowlevelkeyhookinjected-0/54638435#54638435
    def __init__(self):
        pass

    def PressKey(self, hexKeyCode):
        x = INPUT(type=INPUT_KEYBOARD,
                  ki=KEYBDINPUT(wVk=hexKeyCode))
        user32.SendInput(1, ctypes.byref(x), ctypes.sizeof(x))

    def ReleaseKey(self, hexKeyCode):
        x = INPUT(type=INPUT_KEYBOARD,
                  ki=KEYBDINPUT(wVk=hexKeyCode,
                                dwFlags=KEYEVENTF_KEYUP))
        user32.SendInput(1, ctypes.byref(x), ctypes.sizeof(x))

    def push_space(self):
        self.PressKey(0x20)
        time.sleep((random.random() + 1.0) * self.PRESS_TIME)  # human-like
        self.ReleaseKey(0x20)


class HardKbMouse:
    ENTER_OPERATION = '\r\n'
    LINUX_ENTER_OPERATION = '\n'
    INFO = '[INFO] '
    ERROR = '[ERROR] '
    PROG = '[PROGRESS]'
    ENCODING = 'utf-8'
    SPACE_KEY = 44
    PAUSE = 0.005
    PRESS_TIME = 100  # ms

    # 完整发送应答
    def _UartSendCmdWaitforAsk(self, content: str, timeout=10):
        control_c = '\003'
        send = bytes(content + self.ENTER_OPERATION, self.ENCODING)
        return_content = ""
        self.session.write(send)
        time.sleep(self.PAUSE)
        while True:
            response = self.session.read(self.session.in_waiting).decode(self.ENCODING)
            if response:
                return_content += response
            if '>>>' in response:
                return True, return_content
            elif '...' in response:
                self.session.write(bytes(control_c, self.ENCODING))
                time.sleep(self.PAUSE)
                self.session.write(send)
                time.sleep(self.PAUSE)
            else:
                time.sleep(self.PAUSE)
                timeout -= 1
                if timeout <= 0:
                    return False, return_content

    def __init__(self, com_name: str):
        # 连接开发板
        self.session = serial.Serial(com_name, 115200)
        status, response = self._UartSendCmdWaitforAsk('km.version()', 100)
        if status:
            print(self.INFO, response.replace(self.ENTER_OPERATION, ''))
        else:
            raise serial.serialutil.SerialException(self.ERROR,
                                                    "could not open port {}: FileNotFoundError(2, '系统找不到指定的文件。', None, 2)".format(
                                                        com_name))

    def push_space(self):
        random_pressing = int((random.random() + 1.0) * self.PRESS_TIME)  # ms, human-like
        status, response = self._UartSendCmdWaitforAsk('km.press({},{})'.format(self.SPACE_KEY, random_pressing), 100)
        if status:
            print(self.PROG, "执行完毕".format(response))
        else:
            print(self.ERROR, "执行脚本出错, info: {}".format(response))


class DodgingTrigger(GameAudioListener):
    threshold = 0.10
    monitor_time = 5  # 秒

    def __init__(self, sample_path: str, simulator, is_monitor=False):
        self.simulator = simulator
        self.is_monitor = is_monitor
        if self.is_monitor:
            self.len_samples = int(self.monitor_time / self.sample_len)
            self.monitor = WaveMonitor(self.len_samples, self.threshold)
            self.monitor_array = np.zeros(shape=(self.len_samples,), dtype=np.float64)
        super().__init__(sample_path)

    def online_listening(self):
        print("开始监测")

        last_frames = np.empty(shape=(0,), dtype=np.float64)
        is_past_triggered = False

        with self.audio_instance as audio_recorder:
            while True:
                current_frame = np.empty(shape=(0,), dtype=np.float64)
                for index in range(int(self.used_sr / self.chunk_size * self.sample_len)):
                    stream_data = audio_recorder.record(numframes=self.chunk_size)
                    read_chunks = librosa.to_mono(stream_data.T)

                    current_frame = np.append(current_frame, read_chunks)

                # 积累完成,计算匹配分数
                combined_frames = np.append(last_frames, current_frame)
                max_score = self.matching(combined_frames)
                if self.is_monitor:
                    self.monitor_array[:-1] = self.monitor_array[1:]
                    self.monitor_array[-1] = max_score
                    self.monitor.update_array(self.monitor_array)

                if max_score >= self.threshold:
                    # if not is_past_triggered:  # 应该可以连续激发
                    self.simulator.push_space()  # 触发动作
                    trigger_text = "触发分数: {}".format(round(max_score, 5))
                    self.monitor.update_message(trigger_text)
                    print(trigger_text)

                    is_past_triggered = True
                else:
                    is_past_triggered = False

                last_frames = current_frame
