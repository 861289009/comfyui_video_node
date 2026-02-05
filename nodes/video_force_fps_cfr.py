# -*- coding: utf-8 -*-

import os
import uuid
import subprocess

from .video_file import VideoFile
from .ffmpeg_util import resolve_ffmpeg


class VideoForceFpsCfr:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "video": ("VIDEO",),
                "force_fps": ("INT", {"default": 30, "min": 1, "max": 240, "step": 1}),
            }
        }

    RETURN_TYPES = ("VIDEO",)
    RETURN_NAMES = ("video",)
    FUNCTION = "convert"
    CATEGORY = "Tools/Video"

    def convert(self, video, force_fps):
        try:
            import folder_paths
            output_dir = folder_paths.get_output_directory()
        except Exception:
            output_dir = os.getcwd()

        os.makedirs(output_dir, exist_ok=True)
        uid = uuid.uuid4().hex
        src_path = os.path.join(output_dir, f"{uid}_input.mp4")
        out_path = os.path.join(output_dir, f"{uid}_{int(force_fps)}fps.mp4")

        if hasattr(video, "_VideoFromFile__file"):
            src_path = getattr(video, "_VideoFromFile__file")
        elif hasattr(video, "save_to"):
            video.save_to(src_path)
        else:
            raise RuntimeError("video 输入不支持：需要可 save_to 的视频对象")

        if not os.path.exists(src_path):
            raise RuntimeError("视频保存失败")

        subprocess.run(
            [
                resolve_ffmpeg(),
                "-y",
                "-i",
                src_path,
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
                out_path,
            ],
            check=True,
        )

        return (VideoFile(out_path),)
