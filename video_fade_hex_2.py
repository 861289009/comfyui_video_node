import torch

# ===============================
# 工具函数
# ===============================

def hex_to_rgb01(hex_color: str, device):
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
    elif curve == "ease_in":
        return t * t
    elif curve == "ease_out":
        return 1.0 - (1.0 - t) * (1.0 - t)
    return t


# ===============================
# 节点定义
# ===============================

class VideoFadeHex2In:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images_a": ("IMAGE",),
                "images_b": ("IMAGE",),
                "fade_frames": ("INT", {"default": 20, "min": 1, "max": 300}),
                "hold_frames": ("INT", {"default": 10, "min": 0, "max": 300}),
                "fade_curve": (["linear", "ease_in", "ease_out"],),
                "color_hex": ("STRING", {"default": "#000000"}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "run"
    CATEGORY = "video/transition"

    def run(
        self,
        images_a,
        images_b,
        fade_frames,
        hold_frames,
        fade_curve,
        color_hex,
    ):
        device = images_a.device
        color_rgb = hex_to_rgb01(color_hex, device)

        output = []

        len_a = images_a.shape[0]
        len_b = images_b.shape[0]

        # ---------- A 正常播放 ----------
        play_a = max(0, len_a - fade_frames)
        for i in range(play_a):
            output.append(images_a[i])

        # ---------- 构造颜色帧（关键修复点） ----------
        H, W, C = images_a[0].shape
        color_frame = color_rgb.view(1, 1, 3).expand(H, W, 3)

        # ---------- A → Color ----------
        for i in range(fade_frames):
            t = i / max(1, fade_frames - 1)
            wgt = curve_weight(t, fade_curve)

            a_frame = safe_get(images_a, play_a + i)
            out = a_frame * (1.0 - wgt) + color_frame * wgt
            output.append(out)

        # ---------- Color Hold ----------
        for _ in range(hold_frames):
            output.append(color_frame)

        # ---------- Color → B（B 同步推进，不暂停） ----------
        for i in range(fade_frames):
            t = i / max(1, fade_frames - 1)
            wgt = curve_weight(t, fade_curve)

            b_frame = safe_get(images_b, i)
            out = color_frame * (1.0 - wgt) + b_frame * wgt
            output.append(out)

        # ---------- B 剩余 ----------
        for i in range(fade_frames, len_b):
            output.append(images_b[i])

        if len(output) == 0:
            output.append(images_a[0])

        return (torch.stack(output, dim=0),)


# ===============================
# 注册
# ===============================

NODE_CLASS_MAPPINGS = {
    "VideoFadeHex2In": VideoFadeHex2In,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "VideoFadeHex2In": "Video Fade Hex (2 Inputs, No Pause)",
}
