# ComfyUI Video Fade Hex 2

一个 ComfyUI 节点，用于在两个视频片段（或图像序列）之间创建平滑过渡效果。它通过淡出到指定的十六进制颜色，保持一段时间，然后淡入到第二个视频片段来实现过渡。

## 功能特点

- **颜色过渡**：支持自定义过渡颜色（Hex 格式，如 `#000000` 黑色）。
- **灵活控制**：可配置淡入/淡出帧数 (`fade_frames`) 和中间颜色保持帧数 (`hold_frames`)。
- **平滑曲线**：支持多种缓动曲线 (`linear`, `ease_in`, `ease_out`)，让过渡更自然。
- **自动拼接**：自动将输入 A、过渡片段和输入 B 拼接成完整的输出序列。

## 输入参数

- **images_a**: 第一段视频或图像序列。
- **images_b**: 第二段视频或图像序列。
- **fade_frames**: 淡入/淡出的帧数（默认 24）。
- **hold_frames**: 中间颜色保持的帧数（默认 0）。
- **color_hex**: 过渡颜色的十六进制代码（默认 `#000000`）。
- **curve**: 缓动曲线类型 (`linear`, `ease_in`, `ease_out`)。

## 安装方法

1.  将本仓库克隆到你的 ComfyUI `custom_nodes` 目录下：
    ```bash
    cd ComfyUI/custom_nodes
    git clone https://github.com/861289009/comfyui_video_node.git
    ```
2.  重启 ComfyUI。

## 示例

将两个加载了视频的节点分别连接到 `images_a` 和 `images_b`，设置你喜欢的颜色和帧数，即可生成带有颜色过渡的完整视频。
