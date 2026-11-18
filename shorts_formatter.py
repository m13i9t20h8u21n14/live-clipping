"""
Shorts Formatter: High-speed 9:16 (1080x1920) vertical YouTube Shorts converter.
Optimized for NVIDIA RTX 4060 GPU (NVENC) with zero Whisper lag.
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
        Processes raw video into 1080x1920 vertical Short at lightning speed using GPU NVENC.
        No Whisper model or subtitle overhead.
        """
        output_filename = f"short_{input_clip.stem}_{layout}.mp4"
        output_path = self.output_dir / output_filename

        print(f"[ShortsFormatter] Formatting clip '{input_clip.name}' via GPU (Layout: '{layout}')...")

        if layout == "blur_fill":
            # Fast downscaled background blur + crisp centered gameplay overlay
            filter_complex = (
                "[0:v]scale=270:480:force_original_aspect_ratio=increase,"
                "crop=270:480,boxblur=10:1,scale=1080:1920[bg];"
                "[0:v]scale=1080:-2[fg];"
                "[bg][fg]overlay=(W-w)/2:(H-h)/2[v]"
            )
        elif layout == "split_cam_top":
            filter_complex = (
                "[0:v]crop=in_w*0.30:in_h*0.35:in_w*0.70:0,scale=1080:672[cam];"
                "[0:v]crop=in_w:in_h*0.65:0:in_h*0.35,scale=1080:1248[game];"
                "[cam][game]vstack=inputs=2[v]"
            )
        else: # center_crop
            filter_complex = "[0:v]scale=-2:1920,crop=1080:1920[v]"

        # Prefer NVIDIA NVENC hardware encoder (RTX 4060)
        cmd_nvenc = [
            "ffmpeg", "-hide_banner", "-loglevel", "error",
            "-i", str(input_clip),
            "-filter_complex", filter_complex,
            "-map", "[v]",
            "-map", "0:a?",
            "-c:v", "h264_nvenc",
            "-preset", "p4",
            "-cq", "23",
            "-c:a", "aac",
            "-b:a", "192k",
            "-y", str(output_path)
        ]

        res = subprocess.run(cmd_nvenc)

        # Fallback to CPU ultrafast if GPU fails
        if res.returncode != 0 or not output_path.exists():
            print("[ShortsFormatter] NVENC unavailable, falling back to CPU ultrafast...")
            cmd_cpu = [
                "ffmpeg", "-hide_banner", "-loglevel", "error",
                "-i", str(input_clip),
                "-filter_complex", filter_complex,
                "-map", "[v]",
                "-map", "0:a?",
                "-c:v", "libx264",
                "-preset", "ultrafast",
                "-crf", "22",
                "-c:a", "aac",
                "-b:a", "192k",
                "-y", str(output_path)
            ]
            res = subprocess.run(cmd_cpu)

        if res.returncode == 0 and output_path.exists() and output_path.stat().st_size > 0:
            print(f"[ShortsFormatter] Short ready in output_clips: {output_path.name}")
            return output_path
        else:
            print("[ShortsFormatter] Error formatting video.")
            return None
