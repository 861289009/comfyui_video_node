# -*- coding: utf-8 -*-


def hex_to_rgb01(hex_color: str, device):
    import torch

    hex_color = hex_color.lstrip("#")
    if len(hex_color) != 6:
        raise ValueError("color_hex must be like #RRGGBB")
    r = int(hex_color[0:2], 16) / 255.0
    g = int(hex_color[2:4], 16) / 255.0
    b = int(hex_color[4:6], 16) / 255.0
    return torch.tensor([r, g, b], dtype=torch.float32, device=device)


def safe_get(frames, idx):
    if idx < 0:
        return frames[0]
    if idx >= len(frames):
        return frames[-1]
    return frames[idx]


def curve_weight(t, curve):
    if curve == "linear":
        return t
    if curve == "ease_in":
        return t * t
    if curve == "ease_out":
        return 1.0 - (1.0 - t) * (1.0 - t)
    return t


from .ffmpeg_util import resolve_ffmpeg
from .video_file import VideoFile


def _decode_video_to_tensor_list(path, device):
    try:
        import av
        import numpy as np
        import torch
        import cv2
    except Exception as e:
        raise RuntimeError("缺少依赖：av、numpy、torch") from e

    container = av.open(path)
    try:
        stream = next((s for s in container.streams if s.type == "video"), None)
        if stream is None:
            raise RuntimeError("未找到视频流")
        fps = None
        if stream.average_rate:
            fps = float(stream.average_rate)
        elif stream.base_rate:
            fps = float(stream.base_rate)
        rotate_tag = "0"
        try:
            rotate_tag = stream.metadata.get("rotate", "0")
        except Exception:
            rotate_tag = "0"
        try:
            rotate = int(str(rotate_tag).strip())
        except Exception:
            rotate = 0
        frames = []
        for frame in container.decode(video=0):
            img = frame.to_ndarray(format="rgb24")
            if rotate == 90:
                img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
            elif rotate == 180:
                img = cv2.rotate(img, cv2.ROTATE_180)
            elif rotate == 270:
                img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
            img_t = torch.from_numpy(img).to(device).float() / 255.0
            frames.append(img_t)
        return frames, fps
    finally:
        container.close()


class VideoFadeHex2In:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "video_a": ("VIDEO",),
                "video_b": ("VIDEO",),
                "fade_frames": ("INT", {"default": 20, "min": 1, "max": 300}),
                "hold_frames": ("INT", {"default": 10, "min": 0, "max": 300}),
                "fade_curve": (["linear", "ease_in", "ease_out"],),
                "color_hex": ("STRING", {"default": "#000000"}),
            }
        }

    RETURN_TYPES = ("VIDEO",)
    RETURN_NAMES = ("video",)
    FUNCTION = "run"
    CATEGORY = "Tools/Video"

    def run(self, video_a, video_b, fade_frames, hold_frames, fade_curve, color_hex):
        import os
        import uuid
        import torch
        import numpy as np
        import cv2
        try:
            import folder_paths
            out_dir = folder_paths.get_output_directory()
        except Exception:
            out_dir = os.getcwd()

        os.makedirs(out_dir, exist_ok=True)
        uid = uuid.uuid4().hex
        a_path = os.path.join(out_dir, f"{uid}_a.mp4")
        b_path = os.path.join(out_dir, f"{uid}_b.mp4")
        out_video = os.path.join(out_dir, f"{uid}_fade_hex.mp4")
        tmp_frames_dir = os.path.join(out_dir, f"{uid}_frames")
        os.makedirs(tmp_frames_dir, exist_ok=True)

        if hasattr(video_a, "_VideoFromFile__file"):
            a_path = getattr(video_a, "_VideoFromFile__file")
        else:
            video_a.save_to(a_path)
        if hasattr(video_b, "_VideoFromFile__file"):
            b_path = getattr(video_b, "_VideoFromFile__file")
        else:
            video_b.save_to(b_path)

        device = torch.device("cpu")
        frames_a, fps_a = _decode_video_to_tensor_list(a_path, device)
        frames_b, fps_b = _decode_video_to_tensor_list(b_path, device)
        fps = float(fps_a or fps_b or 30.0)

        # match resolution to A
        h, w, _ = frames_a[0].shape
        # ensure even dimensions for yuv420p
        if h % 2 != 0:
            h = h - 1
        if w % 2 != 0:
            w = w - 1
        def resize_to_hw(img):
            arr = (img.cpu().numpy() * 255.0).astype(np.uint8)
            arr = cv2.resize(arr, (w, h), interpolation=cv2.INTER_AREA)
            return torch.from_numpy(arr).float() / 255.0
        frames_a = [resize_to_hw(f) for f in frames_a]
        frames_b = [resize_to_hw(f) for f in frames_b]

        color_rgb = hex_to_rgb01(color_hex, device)
        color_frame = color_rgb.view(1, 1, 3).expand(h, w, 3)

        output = []
        len_a = len(frames_a)
        len_b = len(frames_b)

        play_a = max(0, len_a - fade_frames)
        for i in range(play_a):
            output.append(frames_a[i])

        for i in range(fade_frames):
            t = i / max(1, fade_frames - 1)
            wgt = curve_weight(t, fade_curve)
            a_frame = safe_get(frames_a, play_a + i)
            out = a_frame * (1.0 - wgt) + color_frame * wgt
            output.append(out)

        for _ in range(hold_frames):
            output.append(color_frame)

        for i in range(fade_frames):
            t = i / max(1, fade_frames - 1)
            wgt = curve_weight(t, fade_curve)
            b_frame = safe_get(frames_b, i)
            out = color_frame * (1.0 - wgt) + b_frame * wgt
            output.append(out)

        for i in range(fade_frames, len_b):
            output.append(frames_b[i])

        if len(output) == 0:
            output.append(frames_a[0])

        # write frames
        for i, img in enumerate(output):
            arr = (img.cpu().numpy() * 255.0).astype(np.uint8)
            cv2.imwrite(os.path.join(tmp_frames_dir, f"frame_{i:05d}.png"), cv2.cvtColor(arr, cv2.COLOR_RGB2BGR))

        # encode video (no audio)
        import subprocess
        subprocess.run(
            [
                resolve_ffmpeg(),
                "-y",
                "-framerate",
                str(int(round(fps))),
                "-i",
                os.path.join(tmp_frames_dir, "frame_%05d.png"),
                "-c:v",
                "libx264",
                "-pix_fmt",
                "yuv420p",
                "-r",
                str(int(round(fps))),
                "-vsync",
                "cfr",
                "-movflags",
                "+faststart",
                out_video,
            ],
            check=True,
        )

        return (VideoFile(out_video),)
