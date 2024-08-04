# ZZZSoundTrigger
Dodging Trigger for ZZZ based on waveframe

## 使用

下载：`git clone https://github.com/ImLaoBJie/ZZZSoundTrigger.git`

环境安装：`pip install -r requirements.txt`

运行, 管理员身份运行shell/cmd：`python Main.py`

## 参数说明
`SAMPLE_PATH`: 特征波形音乐文件位置

`THRESHOLD`: 触发动作阈值，默认0.1

`EXPANSION_RATIO`: 最大归一化交叉相关 (MAXIMUM NORMALIZED CROSS-CORRELATE) 的倍数，默认1.0

`IS_ALLOW_SUCCESSIVE_TRIGGER`: 是否可以连续触发，默认不可以`False` (防止连续触发)

`ACTION`: 格挡 (`'push_space'`)或者双闪 (`'double_dodge'`)，默认格挡，由于音频识别无法识别红光，因此双闪的效果并不好，即红光闪避后会切人，不建议使用

## 原理说明
演示视频：[Bilibili](https://www.bilibili.com/video/BV1MT421r73n/)
