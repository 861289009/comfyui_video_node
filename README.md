# Comfy 自定义节点脚本仓库

用于存放编写的 ComfyUI 自定义节点脚本（custom nodes），主要包含视频处理与视频转场相关节点。

## 安装

将本仓库放到 ComfyUI 的 `custom_nodes` 目录下，例如：

- `ComfyUI/custom_nodes/<本仓库目录>`

重启 ComfyUI 后即可加载。

## 环境与依赖

- ffmpeg：仓库内置并优先使用 Windows 版 ffmpeg（默认路径：`tools/bin_ffmpeg/bin/ffmpeg.exe`）。若未随仓库附带，请将 `ffmpeg.exe` 放到以下任意位置（推荐第一个）：
  - `tools/bin_ffmpeg/bin/ffmpeg.exe`
  - `tools/bin_ffmpeg/ffmpeg.exe`
  - 或将 ffmpeg 加入系统 `PATH`，或设置环境变量 `FFMPEG_PATH` 指向 `ffmpeg.exe`
- Python 依赖：`av`、`numpy`、`pillow`、`opencv-python`、`torch`
- 环境自检：在仓库根运行 `python tools/env_check.py`，将输出 ffmpeg 路径与依赖版本

### Tools/Video

- Video Probe (Frames/FPS/Duration)（`VideoProbe`）
  - 输入：`video: VIDEO`
  - 输出：`frame_count: INT`、`fps: FLOAT`、`duration_sec: FLOAT`
  - 说明：探测视频总帧数、帧率与时长（依赖 PyAV）

- Video First Frame（`VideoFirstFrame`）
  - 输入：`video: VIDEO`
  - 输出：`image: IMAGE`
  - 说明：抽取视频首帧输出为 IMAGE（依赖 OpenCV、PyTorch）

- Video Split (CFR)（`VideoUrlSplitCfr`）
  - 输入：`video: VIDEO`、`cut_sec: FLOAT`、`force_fps: INT`
  - 输出：`video1: VIDEO`、`video2: VIDEO`
  - 说明：切两段；第一段 copy，第二段转为指定 CFR（依赖 ffmpeg）

- Video Last Frame（`VideoUrlLastFrame`）
  - 输入：`video: VIDEO`、`end_offset_sec: FLOAT`
  - 输出：`image: IMAGE`
  - 说明：从结尾向前取 `end_offset_sec` 秒处的画面并输出 IMAGE（依赖 ffmpeg、Pillow、numpy、PyTorch）

- Video Merge (30fps CFR, No Audio)（`VideoMerge30FpsNoAudio`）
  - 输入：`video1: VIDEO`、`video2: VIDEO`
  - 输出：`video: VIDEO`
  - 说明：两段视频统一为 30fps CFR、去音频后无缝拼接（依赖 ffmpeg）

- Video Merge (30fps CFR, With Audio)（`VideoMerge30FpsAudio`）
  - 输入：`video1: VIDEO`、`video2: VIDEO`
  - 输出：`video: VIDEO`
  - 说明：两段视频统一为 30fps CFR + AAC 后无缝拼接并保留音频（依赖 ffmpeg）

- Video Add Audio (AAC)（`VideoAddAudio`）
  - 输入：`video: VIDEO`、`audio: *`
  - 输出：`video: VIDEO`
  - 说明：将音频混入视频，视频流 copy，音频编码为 AAC（依赖 ffmpeg；audio 支持可保存对象 / 本地路径 / `{waveform,sample_rate}`）

- Video Trim Start Frames（`VideoTrimStartFrames`）
  - 输入：`video: VIDEO`、`trim_frames: INT`
  - 输出：`video: VIDEO`
  - 说明：裁剪视频开头 `trim_frames` 帧（依赖 PyAV、ffmpeg；当前输出为无音频视频流；内部按 `-ss` 进行秒级精确裁剪）

- Video Trim End Frames（`VideoTrimEndFrames`）
  - 输入：`video: VIDEO`、`trim_frames: INT`
  - 输出：`video: VIDEO`
  - 说明：裁剪视频结尾 `trim_frames` 帧（依赖 PyAV、ffmpeg；当前输出为无音频视频流；内部按 `-t` 保留前段时长）

- Video Fade Hex (2 Inputs, No Pause)（`VideoFadeHex2In`）
  - 输入：`video_a: VIDEO`、`video_b: VIDEO`、`fade_frames: INT`、`hold_frames: INT`、`fade_curve: (linear|ease_in|ease_out)`、`color_hex: STRING`
  - 输出：`video: VIDEO`
  - 说明：A → 颜色帧 → B 的淡入淡出转场；B 不暂停同步推进。内部逐帧计算（PyAV/torch），分辨率统一到 A，并使用 ffmpeg 编码为 CFR 视频（不含音频）。

- Video Force FPS (CFR)（`VideoForceFpsCfr`）
  - 输入：`video: VIDEO`、`force_fps: INT`
  - 输出：`video: VIDEO`
  - 说明：将输入视频转为指定帧率的 CFR（libx264 + yuv420p），音频编码为 AAC。
  
 

### 参数与注意事项

- VideoUrlSplitCfr
  - `cut_sec`：从该秒处切分，前段 copy，后段转为 `force_fps` 的 CFR
  - `force_fps`：后段强制帧率（整数），常用 30/60
  - 需要 ffmpeg；若未找到会在报错中列出可用路径
- VideoTrimStartFrames / VideoTrimEndFrames
  - `trim_frames` 必须小于视频总帧数
  - 内部先以 PyAV 读取帧数与 fps，再用 ffmpeg 做时间裁剪（更稳健）
- VideoFadeHex2In
  - `fade_curve`：`linear` 线性、`ease_in` 先慢后快、`ease_out` 先快后慢
  - 分辨率按 A 统一；输出不含音频（可用 AddAudio 或 MergeAudio 追加）
- VideoAddAudio
  - `audio` 可为可保存对象、文件路径或 `{waveform, sample_rate}` 字典
  - 视频流 `copy`，音频编码 `aac`，采样率 48k，双声道