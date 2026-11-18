"""
Shorts Formatter: Converts horizontal 16:9 gaming clips into 9:16 (1080x1920) vertical YouTube Shorts
and burns bold yellow subtitles automatically without path parsing errors.
"""
import os
import time
import subprocess
from pathlib import Path
from config import OUTPUT_DIR, DEFAULT_LAYOUT

class ShortsFormatter:
    def __init__(self, output_dir: Path = OUTPUT_DIR, enable_subtitles: bool = True):
        self.output_dir = output_dir
        self.enable_subtitles = enable_subtitles

    def format_to_short(self, input_clip: Path, title_tag: str = "GTA 6 LIVE", layout: str = DEFAULT_LAYOUT) -> Path:
        """
        Processes raw video into 1080x1920 vertical Short with bold yellow subtitles.
        """
        output_filename = f"short_{input_clip.stem}_{layout}.mp4"
        output_path = self.output_dir / output_filename
        
        # Use a local relative path in current working directory to prevent Windows drive letter (C:) & space parsing bugs in FFmpeg
        temp_ass_path = Path(f"temp_sub_{int(time.time())}.ass")

        print(f"[ShortsFormatter] Formatting clip using layout: '{layout}'...")

        # 1. Generate Bold Yellow Subtitles if speech is present
        has_subs = False
        if self.enable_subtitles:
            try:
                from subtitles import SubtitleGenerator
                sub_gen = SubtitleGenerator(model_size="tiny")
                has_subs = sub_gen.generate_ass(input_clip, temp_ass_path)
            except Exception as e:
                print(f"[ShortsFormatter] Subtitle note: {e}")

        # 2. Build FFmpeg Filter Complex with relative filename
        ass_filter = ""
        if has_subs and temp_ass_path.exists():
            ass_filter = f",ass={temp_ass_path.name}"

        if layout == "blur_fill":
            filter_complex = (
                f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,"
                f"crop=1080:1920,boxblur=25:5[bg];"
                f"[0:v]scale=1080:-2[fg];"
                f"[bg][fg]overlay=(W-w)/2:(H-h)/2{ass_filter}[v]"
            )
        elif layout == "split_cam_top":
            filter_complex = (
                f"[0:v]crop=in_w*0.30:in_h*0.35:in_w*0.70:0,scale=1080:672[cam];"
                f"[0:v]crop=in_w:in_h*0.65:0:in_h*0.35,scale=1080:1248[game];"
                f"[cam][game]vstack=inputs=2{ass_filter}[v]"
            )
        else:
            filter_complex = (
                f"[0:v]scale=-2:1920,crop=1080:1920{ass_filter}[v]"
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

        # Cleanup temp ASS subtitle file
        if temp_ass_path.exists():
            try:
                temp_ass_path.unlink()
            except Exception:
                pass

        if res.returncode == 0 and output_path.exists() and output_path.stat().st_size > 0:
            print(f"[ShortsFormatter] Short rendered successfully: {output_path.name}")
            return output_path
        else:
            print("[ShortsFormatter] Error formatting video.")
            return None
