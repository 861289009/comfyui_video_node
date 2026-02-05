# -*- coding: utf-8 -*-

import os
import subprocess
import uuid
import wave

from .video_file import VideoFile
from .ffmpeg_util import resolve_ffmpeg


class VideoAddAudio:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "video": ("VIDEO",),
                "audio": ("*",),
            }
        }

    RETURN_TYPES = ("VIDEO",)
    RETURN_NAMES = ("video",)
    FUNCTION = "mux"
    CATEGORY = "Tools/Video"

    def mux(self, video, audio):
        if not video:
            raise RuntimeError("video 为空")
        if audio is None:
            raise RuntimeError("audio 为空")

        try:
            import folder_paths

            base_dir = folder_paths.get_output_directory()
        except Exception:
            base_dir = os.getcwd()

        os.makedirs(base_dir, exist_ok=True)
        uid = uuid.uuid4().hex

        video_tmp = os.path.join(base_dir, f"{uid}_video.mp4")
        audio_tmp = os.path.join(base_dir, f"{uid}_audio.wav")
        out_path = os.path.join(base_dir, f"{uid}_mux.mp4")

        video_path = self._resolve_video_path(video, video_tmp)
        audio_path = self._resolve_audio_path(audio, audio_tmp)

        subprocess.run(
            [
                resolve_ffmpeg(),
                "-y",
                "-i",
                video_path,
                "-i",
                audio_path,
                "-map",
                "0:v:0",
                "-map",
                "1:a:0",
                "-c:v",
                "copy",
                "-c:a",
                "aac",
                "-ar",
                "48000",
                "-ac",
                "2",
                "-shortest",
                "-movflags",
                "+faststart",
                out_path,
            ],
            check=True,
        )

        return (VideoFile(out_path),)

    def _resolve_video_path(self, video_in, video_tmp):
        if hasattr(video_in, "save_to"):
            video_in.save_to(video_tmp)
            if not os.path.exists(video_tmp):
                raise RuntimeError("视频保存失败")
            return video_tmp

        raise RuntimeError("无法识别视频类型：" + str(type(video_in)))

    def _resolve_audio_path(self, audio_in, audio_tmp):
        if hasattr(audio_in, "save_to"):
            audio_in.save_to(audio_tmp)
            if not os.path.exists(audio_tmp):
                raise RuntimeError("音频保存失败")
            return audio_tmp

        if isinstance(audio_in, str) and os.path.exists(audio_in):
            return audio_in

        if isinstance(audio_in, dict) and "waveform" in audio_in and "sample_rate" in audio_in:
            waveform = audio_in["waveform"]
            sample_rate = int(audio_in["sample_rate"])

            if hasattr(waveform, "detach"):
                waveform = waveform.detach().cpu().numpy()

            try:
                import numpy as np
            except Exception as e:
                raise RuntimeError("缺少依赖：numpy") from e

            waveform = np.asarray(waveform)
            if waveform.ndim == 0:
                waveform = waveform.reshape(1)
            if waveform.ndim > 1:
                waveform = waveform.reshape(-1)

            self._write_wav_mono_16bit(audio_tmp, waveform, sample_rate)
            return audio_tmp

        raise RuntimeError("无法识别音频类型：" + str(type(audio_in)))

    def _write_wav_mono_16bit(self, path, samples, sample_rate):
        with wave.open(path, "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(int(sample_rate))

            for s in samples:
                if s > 1:
                    s = 1
                if s < -1:
                    s = -1
                wav.writeframesraw(int(s * 32767).to_bytes(2, byteorder="little", signed=True))
