"""
Configuration file for Live Stream Auto-Clipper
Tuned specifically for CarryisLive & GamerFleet.
"""
import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent
BUFFER_DIR = BASE_DIR / "temp_buffer"
OUTPUT_DIR = BASE_DIR / "output_clips"

BUFFER_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# Streamer Quick Presets (1-Click Shortcuts)
STREAMER_PRESETS = {
    "carry": "https://www.youtube.com/@CarryisLive/live",
    "fleet": "https://www.youtube.com/@GamerFleet/live"
}

# Rolling Buffer Settings
SEGMENT_TIME_SECONDS = 4      # Each TS chunk is 4 seconds
BUFFER_TOTAL_SECONDS = 300    # Keep last 5 minutes of live stream (ensures plenty of headroom for 2-minute clips)
MAX_BUFFER_SEGMENTS = BUFFER_TOTAL_SECONDS // SEGMENT_TIME_SECONDS  # 75 segments

# Clip Settings
DEFAULT_CLIP_DURATION = 120   # Duration of clip in seconds (2 minutes)
DEFAULT_LAYOUT = "blur_fill" # 9:16 vertical with blurred background and centered 16:9 gameplay

# Chat Spike Trigger Settings
CHAT_WINDOW_SECONDS = 5       # Analyze chat frequency every 5 seconds
SPIKE_MULTIPLIER = 2.2        # Trigger if messages/sec > 2.2x moving average
COOLDOWN_SECONDS = 120        # Minimum seconds between automatic clips

# Combined High-Energy Indian Gaming Chat Keywords
TRIGGER_KEYWORDS = [
    # CarryisLive specific triggers
    "carry", "rage", "toxic", "gali", "desk", "slap", "chomu", "savage", "pagal", "cheating",
    # GamerFleet specific triggers
    "fleet", "anshu", "choke", "clutch", "oye", "troll", "noob",
    # Universal Indian Hype slang
    "bhai", "op", "khatam", "rip", "lmao", "lol", "wtf", "dead", "sheesh", "w", "omg"
]
