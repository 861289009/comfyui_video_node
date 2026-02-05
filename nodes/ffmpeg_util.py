import os
import shutil


def resolve_ffmpeg():
    base = os.path.dirname(os.path.dirname(__file__))
    candidates = []

    def find_in(folder):
        if not os.path.isdir(folder):
            return None
        for root, dirs, files in os.walk(folder):
            if "ffmpeg.exe" in files:
                return os.path.join(root, "ffmpeg.exe")
        return None

    if os.name == "nt":
        candidates.extend(
            [
                os.path.join(base, "bin_ffmpeg", "bin", "ffmpeg.exe"),
                os.path.join(base, "bin_ffmpeg", "ffmpeg.exe"),
                os.path.join(base, "bin", "ffmpeg.exe"),
                os.path.join(base, "ffmpeg.exe"),
                os.path.join(os.path.dirname(base), "bin_ffmpeg", "bin", "ffmpeg.exe"),
                os.path.join(os.path.dirname(base), "bin_ffmpeg", "ffmpeg.exe"),
                os.path.join(os.path.dirname(base), "ffmpeg", "bin", "ffmpeg.exe"),
            ]
        )

        env_ff = os.environ.get("FFMPEG_PATH") or os.environ.get("FFMPEG_BINARY")
        if env_ff:
            candidates.insert(0, env_ff)

        for p in candidates:
            if p and os.path.exists(p):
                return p

        auto = find_in(os.path.join(base, "bin_ffmpeg"))
        if auto:
            return auto
        auto = find_in(base)
        if auto:
            return auto
        auto = find_in(os.path.dirname(base))
        if auto:
            return auto

        found = shutil.which("ffmpeg")
        if found:
            return found

        msg = "未找到内置或系统 ffmpeg；请将 Windows 版 ffmpeg 放置到以下任一路径：\n" + "\n".join(
            f"- {p}" for p in candidates[:6]
        ) + "\n或将 ffmpeg 加入系统 PATH，或设置环境变量 FFMPEG_PATH 指向 ffmpeg.exe"
        raise RuntimeError(msg)

    # non-Windows: prefer system ffmpeg
    found = shutil.which("ffmpeg")
    if found:
        return found
    raise RuntimeError("未找到系统 ffmpeg，请安装并加入 PATH")
