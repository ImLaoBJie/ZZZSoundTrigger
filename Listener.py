import numpy as np

import librosa
import wave
import soundcard as sc
import soundfile as sf

from time import time

from scipy.signal import correlate
from sklearn.preprocessing import scale


class GameAudioListener:
    used_sr = 32000  # 采样率
    used_channel = 2
    chunk_size = 1600  # 语音块大小
    device_index = 0  # 设备编号
    sample_len = 0.2  # 每次采样长度0.2s

    def __init__(self, sample_path: str, ratio=1.0):
        self.sample_waveform, sample_rate = librosa.load(sample_path)
        self.sample_waveform = librosa.resample(self.sample_waveform, orig_sr=sample_rate, target_sr=self.used_sr)

        # 初始化流监听器
        loopback_speaker = sc.get_microphone(id=str(sc.default_speaker().name), include_loopback=True)
        self.audio_instance = loopback_speaker.recorder(samplerate=self.used_sr, channels=self.used_channel)

        self.ratio = ratio

        print("初始化完毕...")

    def matching(self, stream_waveform: np.ndarray):
        # 标准化
        norm_stream_waveform = scale(stream_waveform, with_mean=False)
        norm_sample_waveform = scale(self.sample_waveform, with_mean=False)

        # 计算NCC
        if norm_stream_waveform.shape[0] > norm_sample_waveform.shape[0]:
            correlation = correlate(norm_stream_waveform, norm_sample_waveform, mode='same', method='fft') / \
                          norm_stream_waveform.shape[0]
        else:
            correlation = correlate(norm_sample_waveform, norm_stream_waveform, mode='same', method='fft') / \
                          norm_sample_waveform.shape[0]

        max_corr = np.max(correlation) * self.ratio

        return max_corr

    def online_listening(self):
        last_frames = np.empty(shape=(0,), dtype=np.float64)

        with self.audio_instance as audio_recorder:
            while True:
                current_frame = np.empty(shape=(0,), dtype=np.float64)
                for index in range(int(self.used_sr / self.chunk_size * self.sample_len)):
                    stream_data = audio_recorder.record(numframes=self.chunk_size)
                    read_chunks = librosa.to_mono(stream_data.T)

                    current_frame = np.append(current_frame, read_chunks)

                # 积累完成,计算匹配分数
                # start_time = time()
                combined_frames = np.append(last_frames, current_frame)
                max_score = self.matching(combined_frames)
                # print("CONSUMED TIME: {}s".format(round(time() - start_time, 8)))

                last_frames = current_frame

                print(max_score, np.max(current_frame))






