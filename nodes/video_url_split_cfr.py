# -*- coding: utf-8 -*-

import os
import subprocess
import uuid
import shutil

from .video_file import VideoFile
from .ffmpeg_util import resolve_ffmpeg


class VideoUrlSplitCfr:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "video": ("VIDEO",),
                "cut_sec": ("FLOAT", {"default": 34.0, "min": 0.0, "step": 0.1}),
                "force_fps": ("INT", {"default": 30, "min": 1, "max": 240, "step": 1}),
            }
        }

    RETURN_TYPES = ("VIDEO", "VIDEO")
    RETURN_NAMES = ("video1", "video2")
    FUNCTION = "split"
    CATEGORY = "Tools/Video"

    def _resolve_ffmpeg(self):
        return resolve_ffmpeg()

    def split(self, video, cut_sec, force_fps):
        if video is None:
            raise RuntimeError("video 为空")

        if cut_sec is None or float(cut_sec) < 0:
            raise RuntimeError("cut_sec 必须是 >= 0 的秒数")

        if force_fps is None or int(force_fps) <= 0:
            raise RuntimeError("force_fps 必须是 > 0 的整数")

        try:
            import folder_paths

            output_dir = folder_paths.get_output_directory()
        except Exception:
            output_dir = os.getcwd()

        os.makedirs(output_dir, exist_ok=True)

        uid = uuid.uuid4().hex
        src_path = os.path.join(output_dir, f"{uid}_input.mp4")
        out1 = os.path.join(output_dir, f"{uid}_part1.mp4")
        out2 = os.path.join(output_dir, f"{uid}_part2_{int(force_fps)}fps.mp4")

        if hasattr(video, "_VideoFromFile__file"):
            src_path = getattr(video, "_VideoFromFile__file")
        elif hasattr(video, "save_to"):
            video.save_to(src_path)
        else:
            raise RuntimeError("video 输入不支持：需要可 save_to 的视频对象")

        if not os.path.exists(src_path):
            raise RuntimeError("视频保存失败")

        try:
            subprocess.run(
                [
                    self._resolve_ffmpeg(),
                "-y",
                "-i",
                src_path,
                "-t",
                str(float(cut_sec)),
                "-map",
                "0:v:0",
                "-map",
                "0:a?",
                "-c:v",
                "copy",
                "-c:a",
                "aac",
                "-movflags",
                "+faststart",
                out1,
                ],
                check=True,
            )
        except FileNotFoundError as e:
            raise RuntimeError("未找到 ffmpeg 可执行文件：请安装并配置 PATH 或 FFMPEG_PATH") from e

        try:
            subprocess.run(
                [
                    self._resolve_ffmpeg(),
                "-y",
                "-ss",
                str(float(cut_sec)),
                "-i",
                src_path,
                "-map",
                "0:v:0",
                "-map",
                "0:a?",
                "-c:v",
                "libx264",
                "-pix_fmt",
                "yuv420p",
                "-r",
                str(int(force_fps)),
                "-vsync",
                "cfr",
                "-c:a",
                "aac",
                "-ar",
                "48000",
                "-ac",
                "2",
                "-movflags",
                "+faststart",
                out2,
                ],
                check=True,
            )
        except FileNotFoundError as e:
            raise RuntimeError("未找到 ffmpeg 可执行文件：请安装并配置 PATH 或 FFMPEG_PATH") from e

        return (VideoFile(out1), VideoFile(out2))
