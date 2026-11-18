"""
Configuration file for Live Stream Auto-Clipper
"""
import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent
BUFFER_DIR = BASE_DIR / "temp_buffer"
OUTPUT_DIR = BASE_DIR / "output_clips"

BUFFER_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# Rolling Buffer Settings
SEGMENT_TIME_SECONDS = 4      # Each TS chunk is 4 seconds
BUFFER_TOTAL_SECONDS = 180    # Keep last 3 minutes of live stream
MAX_BUFFER_SEGMENTS = BUFFER_TOTAL_SECONDS // SEGMENT_TIME_SECONDS  # 45 segments

# Clip Settings
DEFAULT_CLIP_DURATION = 45   # Duration of short in seconds (e.g., last 45s)

# Layout Presets:
# 'blur_fill': 9:16 vertical with blurred background and centered 16:9 gameplay (universal)
# 'split_cam_top': Streamer facecam cropped at top, gameplay at bottom
# 'center_crop': Direct 9:16 center crop
DEFAULT_LAYOUT = "blur_fill"

# Chat Spike Trigger Settings
CHAT_WINDOW_SECONDS = 5       # Analyze chat frequency every 5 seconds
SPIKE_MULTIPLIER = 2.2        # Trigger if messages/sec > 2.2x the moving average
TRIGGER_KEYWORDS = [
    "omg", "w", "lmao", "lol", "wtf", "clip", "no way",
    "holy", "insane", "crazy", "dead", "rip", "pog", "sheesh"
]
COOLDOWN_SECONDS = 90         # Minimum seconds between automatic clips
