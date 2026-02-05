from .video_probe import VideoProbe
from .video_first_frame import VideoFirstFrame
from .video_url_split_cfr import VideoUrlSplitCfr
from .video_url_last_frame import VideoUrlLastFrame
from .video_merge_30fps_noaudio import VideoMerge30FpsNoAudio
from .video_merge_30fps_audio import VideoMerge30FpsAudio
from .video_add_audio import VideoAddAudio
from .video_trim_start_frames import VideoTrimStartFrames
from .video_trim_end_frames import VideoTrimEndFrames
from .video_fade_hex_2in import VideoFadeHex2In
from .video_force_fps_cfr import VideoForceFpsCfr
 

NODE_CLASS_MAPPINGS = {
    "VideoProbe": VideoProbe,
    "VideoFirstFrame": VideoFirstFrame,
    "VideoUrlSplitCfr": VideoUrlSplitCfr,
    "VideoUrlLastFrame": VideoUrlLastFrame,
    "VideoMerge30FpsNoAudio": VideoMerge30FpsNoAudio,
    "VideoMerge30FpsAudio": VideoMerge30FpsAudio,
    "VideoAddAudio": VideoAddAudio,
    "VideoTrimStartFrames": VideoTrimStartFrames,
    "VideoTrimEndFrames": VideoTrimEndFrames,
    "VideoFadeHex2In": VideoFadeHex2In,
    "VideoForceFpsCfr": VideoForceFpsCfr,
 
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "VideoProbe": "Video Probe (Frames/FPS)",
    "VideoFirstFrame": "Video First Frame",
    "VideoUrlSplitCfr": "Split Video (CFR)",
    "VideoUrlLastFrame": "Video Last Frame",
    "VideoMerge30FpsNoAudio": "Merge Video (30fps CFR)",
    "VideoMerge30FpsAudio": "Merge Video (30fps + Audio)",
    "VideoAddAudio": "Add Audio to Video (AAC)",
    "VideoTrimStartFrames": "Trim Video Start Frames",
    "VideoTrimEndFrames": "Trim Video End Frames",
    "VideoFadeHex2In": "Video Fade Hex (2 Inputs)",
    "VideoForceFpsCfr": "Force Video FPS (CFR)",
 
}