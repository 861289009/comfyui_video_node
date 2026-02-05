# -*- coding: utf-8 -*-

import os
import uuid


class VideoFirstFrame:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "video": ("VIDEO",),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "extract"
    CATEGORY = "Tools/Video"

    def extract(self, video):
        if video is None:
            raise ValueError("video 为空")

        video_path = None

        if hasattr(video, "_VideoFromFile__file"):
            video_path = getattr(video, "_VideoFromFile__file")

        if not video_path:
            if hasattr(video, "save_to"):
                try:
                    import folder_paths

                    base_dir = folder_paths.get_output_directory()
                except Exception:
                    base_dir = os.getcwd()

                os.makedirs(base_dir, exist_ok=True)
                video_path = os.path.join(base_dir, f"first_frame_{uuid.uuid4().hex}.mp4")
                video.save_to(video_path)
            elif isinstance(video, str) and os.path.exists(video):
                video_path = video

        if not video_path or not os.path.exists(video_path):
            raise RuntimeError("无法获取视频真实路径或保存视频失败")

        try:
            import cv2
        except Exception as e:
            raise RuntimeError("缺少依赖：cv2（OpenCV）") from e

        try:
            import torch
        except Exception as e:
            raise RuntimeError("缺少依赖：torch") from e

        cap = cv2.VideoCapture(video_path)
        try:
            if not cap.isOpened():
                raise RuntimeError("OpenCV 无法打开视频")

            ret, frame = cap.read()
            if not ret or frame is None:
                raise RuntimeError("读取视频首帧失败")
        finally:
            cap.release()

        frame = frame[:, :, ::-1].copy()
        frame = torch.from_numpy(frame).float() / 255.0
        frame = frame.unsqueeze(0)
        frame = frame.cpu()

        return (frame,)
