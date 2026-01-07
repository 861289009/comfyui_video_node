import torch
import math

def hex_to_rgb01(hex_color: str):
    hex_color = hex_color.strip().lstrip("#")
    if len(hex_color) != 6:
        raise ValueError("HEX color must be like #RRGGBB")
    r = int(hex_color[0:2], 16) / 255.0
    g = int(hex_color[2:4], 16) / 255.0
    b = int(hex_color[4:6], 16) / 255.0
    return torch.tensor([r, g, b], dtype=torch.float32)


def ease(t, mode):
    if mode == "linear":
        return t
    if mode == "ease_in":
        return t * t
    if mode == "ease_out":
        return 1 - (1 - t) * (1 - t)
    return t


class VideoFadeHex2:
    """
    Stable IMAGE → IMAGE node
    Always 2 inputs, always 1 IMAGE output
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images_a": ("IMAGE",),
                "images_b": ("IMAGE",),
                "fade_frames": ("INT", {
                    "default": 24,
                    "min": 1,
                    "max": 240,
                    "step": 1
                }),
                "hold_frames": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 240,
                    "step": 1
                }),
                "color_hex": ("STRING", {
                    "default": "#000000"
                }),
                "curve": (["linear", "ease_in", "ease_out"],),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("images",)
    FUNCTION = "process"
    CATEGORY = "video/transition"

    def process(
        self,
        images_a,
        images_b,
        fade_frames,
        hold_frames,
        color_hex,
        curve,
    ):
        device = images_a.device
        dtype = images_a.dtype

        # 基础校验
        if images_a.shape[1:] != images_b.shape[1:]:
            raise ValueError("Image size mismatch between A and B")

        h, w = images_a.shape[1], images_a.shape[2]

        color = hex_to_rgb01(color_hex).to(device=device, dtype=dtype)
        color_frame = color.view(1, 1, 1, 3).expand(1, h, w, 3)

        output = []

        # A 原始帧
        for i in range(images_a.shape[0]):
            output.append(images_a[i:i+1])

        # A → Color
        for i in range(fade_frames):
            t = i / max(fade_frames - 1, 1)
            w1 = 1.0 - ease(t, curve)
            frame = images_a[-1:] * w1 + color_frame * (1.0 - w1)
            output.append(frame)

        # Hold Color
        for _ in range(hold_frames):
            output.append(color_frame)

        # Color → B
        for i in range(fade_frames):
            t = i / max(fade_frames - 1, 1)
            w2 = ease(t, curve)
            frame = color_frame * (1.0 - w2) + images_b[0:1] * w2
            output.append(frame)

        # B 原始帧
        for i in range(images_b.shape[0]):
            output.append(images_b[i:i+1])

        return (torch.cat(output, dim=0),)
