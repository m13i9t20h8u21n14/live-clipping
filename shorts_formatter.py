"""
Shorts Formatter: Converts horizontal 16:9 gaming clips into 9:16 (1080x1920) vertical YouTube Shorts.
"""
import os
import subprocess
from pathlib import Path
from config import OUTPUT_DIR, DEFAULT_LAYOUT

class ShortsFormatter:
    def __init__(self, output_dir: Path = OUTPUT_DIR):
        self.output_dir = output_dir

    def format_to_short(self, input_clip: Path, title_tag: str = "GTA 6 LIVE", layout: str = DEFAULT_LAYOUT) -> Path:
        """
        Processes the raw video into 1080x1920 vertical video using FFmpeg.
        """
        output_filename = f"short_{input_clip.stem}_{layout}.mp4"
        output_path = self.output_dir / output_filename

        print(f"[ShortsFormatter] Formatting clip using layout: '{layout}'...")

        if layout == "blur_fill":
            # 1. Blur Fill: Blurred 9:16 background with sharp 16:9 gameplay centered
            filter_complex = (
                "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,"
                "crop=1080:1920,boxblur=25:5[bg];"
                "[0:v]scale=1080:-1[fg];"
                "[bg][fg]overlay=(W-w)/2:(H-h)/2[v]"
            )
        elif layout == "split_cam_top":
            # 2. Dual Split: Webcam on top (top-right crop assumed), Gameplay bottom
            filter_complex = (
                "[0:v]crop=in_w*0.30:in_h*0.35:in_w*0.70:0,scale=1080:672[cam];"
                "[0:v]crop=in_w:in_h*0.65:0:in_h*0.35,scale=1080:1248[game];"
                "[cam][game]vstack=inputs=2[v]"
            )
        else:
            # 3. Center Crop
            filter_complex = (
                "[0:v]scale=-1:1920,crop=1080:1920[v]"
            )

        cmd = [
            "ffmpeg", "-hide_banner", "-loglevel", "error",
            "-i", str(input_clip),
            "-filter_complex", filter_complex,
            "-map", "[v]",
            "-map", "0:a?",
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-crf", "22",
            "-c:a", "aac",
            "-b:a", "192k",
            "-y", str(output_path)
        ]

        res = subprocess.run(cmd)
        if res.returncode == 0 and output_path.exists() and output_path.stat().st_size > 0:
            print(f"[ShortsFormatter] Short rendered successfully: {output_path}")
            return output_path
        else:
            print("[ShortsFormatter] Error formatting video.")
            return None
