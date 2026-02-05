import os
import sys
import json
import importlib
import shutil
import subprocess


def main():
    sys.path.insert(0, r"e:\comfy_video_node")
    out = {}

    out["FFMPEG_PATH"] = os.environ.get("FFMPEG_PATH")
    out["FFMPEG_BINARY"] = os.environ.get("FFMPEG_BINARY")
    out["PATH_head"] = os.environ.get("PATH", "")[:200]

    try:
        ffm = importlib.import_module("tools.nodes.ffmpeg_util")
        p = ffm.resolve_ffmpeg()
        out["ffmpeg_resolved_path"] = p
        try:
            r = subprocess.run([p, "-version"], capture_output=True, text=True, timeout=5)
            lines = (r.stdout.splitlines() + r.stderr.splitlines())
            out["ffmpeg_version_top"] = lines[0] if lines else ""
        except Exception as e:
            out["ffmpeg_version_error"] = repr(e)
    except Exception as e:
        out["ffmpeg_error"] = repr(e)

    for mod in ["av", "numpy", "PIL", "cv2", "torch"]:
        try:
            m = importlib.import_module(mod)
            v = getattr(m, "__version__", None)
            out[f"{mod}_ok"] = True
            out[f"{mod}_version"] = v
        except Exception as e:
            out[f"{mod}_ok"] = False
            out[f"{mod}_error"] = repr(e)

    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
