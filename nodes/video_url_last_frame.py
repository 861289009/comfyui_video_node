# -*- coding: utf-8 -*-

import os
import subprocess
import uuid

from .ffmpeg_util import resolve_ffmpeg

class VideoUrlLastFrame:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "video": ("VIDEO",),
                "end_offset_sec": ("FLOAT", {"default": 1.0, "min": 0.0, "step": 0.1}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "extract"
    CATEGORY = "Tools/Video"

    def extract(self, video, end_offset_sec):
        if video is None:
            raise RuntimeError("video 为空")

        if end_offset_sec is None or float(end_offset_sec) < 0:
            raise RuntimeError("end_offset_sec 必须是 >= 0 的秒数")

        try:
            import folder_paths

            out_dir = folder_paths.get_output_directory()
        except Exception:
            out_dir = os.getcwd()

        os.makedirs(out_dir, exist_ok=True)

        uid = uuid.uuid4().hex
        video_path = os.path.join(out_dir, f"{uid}_input.mp4")
        last_frame_path = os.path.join(out_dir, f"{uid}_last_frame.png")

        if hasattr(video, "_VideoFromFile__file"):
            video_path = getattr(video, "_VideoFromFile__file")
        elif hasattr(video, "save_to"):
            video.save_to(video_path)
        else:
            raise RuntimeError("video 输入不支持：需要可 save_to 的视频对象")

        if not os.path.exists(video_path):
            raise RuntimeError("视频保存失败")

        subprocess.run(
            [
                resolve_ffmpeg(),
                "-y",
                "-sseof",
                str(-float(end_offset_sec)),
                "-i",
                video_path,
                "-update",
                "1",
                "-q:v",
                "2",
                last_frame_path,
            ],
            check=True,
        )

        if not os.path.exists(last_frame_path):
            raise RuntimeError("尾帧抽取失败")

        try:
            import numpy as np
        except Exception as e:
            raise RuntimeError("缺少依赖：numpy") from e

        try:
            from PIL import Image
        except Exception as e:
            raise RuntimeError("缺少依赖：Pillow") from e

        try:
            import torch
        except Exception as e:
            raise RuntimeError("缺少依赖：torch") from e

        img = Image.open(last_frame_path).convert("RGB")
        img_np = np.array(img).astype(np.float32) / 255.0
        img_tensor = torch.from_numpy(img_np).unsqueeze(0)

        return (img_tensor,)
