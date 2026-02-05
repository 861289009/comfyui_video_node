# -*- coding: utf-8 -*-

import os
import shutil


class VideoFile:
    def __init__(self, file_path):
        self._VideoFromFile__file = file_path
        self.__probe_cache = None

    def save_to(self, dst_path, format=None, **kwargs):
        src_path = self._VideoFromFile__file
        if not isinstance(src_path, str) or not os.path.exists(src_path):
            raise RuntimeError("VideoFile 源路径无效")
        shutil.copyfile(src_path, dst_path)

    def _probe(self):
        if self.__probe_cache is not None:
            return self.__probe_cache
        path = self._VideoFromFile__file
        if not isinstance(path, str) or not os.path.exists(path):
            raise RuntimeError("VideoFile 源路径无效")
        try:
            import av
        except Exception as e:
            raise RuntimeError("缺少依赖：av（PyAV）") from e
        container = av.open(path)
        try:
            stream = next((s for s in container.streams if s.type == "video"), None)
            if stream is None:
                raise RuntimeError("未找到视频流")
            width = getattr(stream, "width", None) or getattr(stream.codec_context, "width", None)
            height = getattr(stream, "height", None) or getattr(stream.codec_context, "height", None)
            fps = None
            if stream.average_rate:
                fps = float(stream.average_rate)
            elif stream.base_rate:
                fps = float(stream.base_rate)
            frames = stream.frames or 0
            if frames <= 0:
                frames = sum(1 for _ in container.decode(video=0))
            duration = None
            if stream.duration and stream.time_base:
                duration = float(stream.duration * stream.time_base)
            elif fps:
                duration = frames / fps
            self.__probe_cache = {
                "width": int(width or 0),
                "height": int(height or 0),
                "fps": float(fps or 0.0),
                "frames": int(frames or 0),
                "duration": float(duration or 0.0),
            }
            return self.__probe_cache
        finally:
            container.close()

    def get_dimensions(self):
        info = self._probe()
        return (info["width"], info["height"])

    def get_fps(self):
        info = self._probe()
        return info["fps"]

    def get_frame_count(self):
        info = self._probe()
        return info["frames"]

    def get_duration(self):
        info = self._probe()
        return info["duration"]
