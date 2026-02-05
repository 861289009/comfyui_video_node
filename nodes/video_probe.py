# -*- coding: utf-8 -*-

import os
import uuid


class VideoProbe:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "video": ("VIDEO",),
            }
        }

    RETURN_TYPES = ("INT", "FLOAT", "FLOAT")
    RETURN_NAMES = ("frame_count", "fps", "duration_sec")
    FUNCTION = "probe"
    CATEGORY = "Tools/Video"

    def probe(self, video):
        try:
            import av
        except Exception as e:
            raise RuntimeError("缺少依赖：av（PyAV）") from e

        try:
            import folder_paths

            base_dir = folder_paths.get_output_directory()
        except Exception:
            base_dir = os.getcwd()

        os.makedirs(base_dir, exist_ok=True)

        video_path = os.path.join(base_dir, f"probe_{uuid.uuid4().hex}.mp4")

        if hasattr(video, "save_to"):
            video.save_to(video_path)
        elif isinstance(video, str) and os.path.exists(video):
            video_path = video
        else:
            raise RuntimeError("video 输入不支持：需要可 save_to 的视频对象或本地文件路径")

        if not os.path.exists(video_path):
            raise RuntimeError("视频保存失败：路径不存在 → " + video_path)

        container = av.open(video_path)
        try:
            stream = next((s for s in container.streams if s.type == "video"), None)
            if stream is None:
                raise RuntimeError("未找到视频流")

            fps = None
            if stream.average_rate:
                fps = float(stream.average_rate)
            elif stream.base_rate:
                fps = float(stream.base_rate)

            total_frames = stream.frames or 0
            if total_frames <= 0:
                total_frames = sum(1 for _ in container.decode(video=0))

            if stream.duration and stream.time_base:
                duration = float(stream.duration * stream.time_base)
            elif fps:
                duration = total_frames / fps
            else:
                duration = 0.0
        finally:
            container.close()

        return (int(total_frames), float(round(fps or 0.0, 4)), float(round(duration, 3)))
