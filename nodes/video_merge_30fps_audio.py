# -*- coding: utf-8 -*-

import os
import subprocess
import uuid

from .video_file import VideoFile
from .ffmpeg_util import resolve_ffmpeg


class VideoMerge30FpsAudio:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "video1": ("VIDEO",),
                "video2": ("VIDEO",),
            }
        }

    RETURN_TYPES = ("VIDEO",)
    RETURN_NAMES = ("video",)
    FUNCTION = "merge"
    CATEGORY = "Tools/Video"

    def merge(self, video1, video2):
        if video1 is None or video2 is None:
            raise RuntimeError("video1 / video2 为空")

        try:
            import folder_paths

            base_dir = folder_paths.get_output_directory()
        except Exception:
            base_dir = os.getcwd()

        os.makedirs(base_dir, exist_ok=True)
        uid = uuid.uuid4().hex

        v1_raw = os.path.join(base_dir, f"{uid}_1_raw.mp4")
        v2_raw = os.path.join(base_dir, f"{uid}_2_raw.mp4")
        v1 = os.path.join(base_dir, f"{uid}_1_30fps_aac.mp4")
        v2 = os.path.join(base_dir, f"{uid}_2_30fps_aac.mp4")
        list_txt = os.path.join(base_dir, f"{uid}_list.txt")
        out_path = os.path.join(base_dir, f"{uid}_merge_30fps_audio.mp4")

        video1.save_to(v1_raw)
        video2.save_to(v2_raw)

        self._normalize_30fps_with_audio(v1_raw, v1)
        self._normalize_30fps_with_audio(v2_raw, v2)

        with open(list_txt, "w", encoding="utf-8") as f:
            f.write("file '" + v1.replace("\\", "/") + "'\n")
            f.write("file '" + v2.replace("\\", "/") + "'\n")

        subprocess.run(
            [
                resolve_ffmpeg(),
                "-y",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                list_txt,
                "-c",
                "copy",
                "-movflags",
                "+faststart",
                out_path,
            ],
            check=True,
        )

        return (VideoFile(out_path),)

    def _normalize_30fps_with_audio(self, src, dst):
        subprocess.run(
            [
                resolve_ffmpeg(),
                "-y",
                "-i",
                src,
                "-map",
                "0:v:0",
                "-map",
                "0:a:0",
                "-c:v",
                "libx264",
                "-pix_fmt",
                "yuv420p",
                "-profile:v",
                "baseline",
                "-level",
                "3.1",
                "-r",
                "30",
                "-vsync",
                "cfr",
                "-g",
                "60",
                "-keyint_min",
                "60",
                "-sc_threshold",
                "0",
                "-c:a",
                "aac",
                "-ar",
                "48000",
                "-ac",
                "2",
                "-movflags",
                "+faststart",
                dst,
            ],
            check=True,
        )
