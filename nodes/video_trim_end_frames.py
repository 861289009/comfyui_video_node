# -*- coding: utf-8 -*-

import os
import subprocess
import uuid

from .video_file import VideoFile
from .ffmpeg_util import resolve_ffmpeg


class VideoTrimEndFrames:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "video": ("VIDEO",),
                "trim_frames": ("INT", {"default": 0, "min": 0, "max": 100000000, "step": 1}),
            }
        }

    RETURN_TYPES = ("VIDEO",)
    RETURN_NAMES = ("video",)
    FUNCTION = "trim"
    CATEGORY = "Tools/Video"

    def trim(self, video, trim_frames):
        if video is None:
            raise RuntimeError("video 为空")

        trim_frames = int(trim_frames)
        if trim_frames < 0:
            raise RuntimeError("trim_frames 必须是 >= 0 的整数")

        try:
            import folder_paths

            base_dir = folder_paths.get_output_directory()
        except Exception:
            base_dir = os.getcwd()

        os.makedirs(base_dir, exist_ok=True)

        uid = uuid.uuid4().hex
        in_path = os.path.join(base_dir, f"{uid}_in.mp4")
        out_path = os.path.join(base_dir, f"{uid}_trim_end_{trim_frames}f.mp4")

        if hasattr(video, "save_to"):
            video.save_to(in_path)
        elif isinstance(video, str) and os.path.exists(video):
            in_path = video
        else:
            raise RuntimeError("video 输入不支持：需要可 save_to 的视频对象或本地文件路径")

        if not os.path.exists(in_path):
            raise RuntimeError("视频保存失败：路径不存在 → " + in_path)

        total_frames, fps = self._probe_frames(in_path)
        if total_frames <= 0:
            raise RuntimeError("无法获取视频帧数")

        keep_frames = total_frames - trim_frames
        if keep_frames <= 0:
            raise RuntimeError("trim_frames 不能 >= 视频总帧数")

        keep_sec = float(keep_frames) / float(fps or 1.0)
        try:
            import subprocess as _sp
            proc = _sp.run(
                [
                    resolve_ffmpeg(),
                    "-y",
                    "-i",
                    in_path,
                    "-t",
                    str(keep_sec),
                    "-map",
                    "0:v:0",
                    "-an",
                    "-vsync",
                    "0",
                    "-c:v",
                    "libx264",
                    "-pix_fmt",
                    "yuv420p",
                    "-movflags",
                    "+faststart",
                    out_path,
                ],
                capture_output=True,
                text=True,
                check=True,
            )
        except Exception as e:
            if hasattr(e, "stderr") and e.stderr:
                raise RuntimeError("ffmpeg 执行失败：\n" + e.stderr) from e
            raise

        return (VideoFile(out_path),)

    def _probe_frames(self, video_path):
        try:
            import av
        except Exception as e:
            raise RuntimeError("缺少依赖：av（PyAV）") from e

        container = av.open(video_path)
        try:
            stream = next((s for s in container.streams if s.type == "video"), None)
            if stream is None:
                return (0, None)

            fps = None
            if stream.average_rate:
                fps = float(stream.average_rate)
            elif stream.base_rate:
                fps = float(stream.base_rate)

            total_frames = stream.frames or 0
            if total_frames <= 0:
                total_frames = sum(1 for _ in container.decode(video=0))

            return (int(total_frames), fps)
        finally:
            container.close()
