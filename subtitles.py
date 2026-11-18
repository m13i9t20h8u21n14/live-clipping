"""
Subtitles Generator: Uses faster-whisper to transcribe speech and generates
high-contrast, bold yellow ASS subtitles styled specifically for YouTube Shorts / TikTok.
"""
import os
import subprocess
from pathlib import Path
from typing import List, Tuple

class SubtitleGenerator:
    def __init__(self, model_size: str = "base"):
        self.model_size = model_size
        self._model = None

    def _get_model(self):
        if self._model is None:
            from faster_whisper import WhisperModel
            print(f"[Subtitles] Loading Whisper model ({self.model_size})...")
            # Run on CPU with INT8 quantization for maximum speed
            self._model = WhisperModel(self.model_size, device="cpu", compute_type="int8")
        return self._model

    def _format_timestamp(self, seconds: float) -> str:
        """Formats seconds to ASS timestamp format: H:MM:SS.cs"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        return f"{hours}:{minutes:02d}:{secs:05.2f}"

    def extract_audio(self, video_path: Path, audio_path: Path):
        cmd = [
            "ffmpeg", "-hide_banner", "-loglevel", "error",
            "-i", str(video_path),
            "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
            "-y", str(audio_path)
        ]
        subprocess.run(cmd)

    def generate_ass(self, video_path: Path, ass_output_path: Path) -> bool:
        """
        Transcribes the video and generates an ASS subtitle file with bold yellow styling.
        """
        audio_temp = video_path.with_suffix(".temp.wav")
        self.extract_audio(video_path, audio_temp)

        if not audio_temp.exists() or audio_temp.stat().st_size == 0:
            return False

        try:
            model = self._get_model()
            segments, info = model.transcribe(
                str(audio_temp),
                word_timestamps=True,
                language="en"
            )

            # ASS Header with Yellow Bold Shorts Style:
            # - Font: Arial Black / Impact
            # - PrimaryColour: &H0000FFFF (Bright Yellow in BGR: B=00, G=FF, R=FF)
            # - OutlineColour: &H00000000 (Black border)
            # - BackColour: &HA0000000 (Soft black drop shadow)
            # - Outline: 5px, Shadow: 3px
            # - Bold: 1, Italic: 1 (slanted dynamic text)
            # - Alignment: 2 (Bottom-center)
            # - MarginV: 420 (Placed right below gameplay/center in 1080x1920)
            ass_content = [
                "[Script Info]",
                "ScriptType: v4.00+",
                "PlayResX: 1080",
                "PlayResY: 1920",
                "",
                "[V4+ Styles]",
                "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
                "Style: YellowShorts,Arial Black,76,&H0000FFFF,&H0000FFFF,&H00000000,&HA0000000,1,1,0,0,100,100,2,0,1,6,3,2,50,50,440,1",
                "",
                "[Events]",
                "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"
            ]

            dialogue_count = 0
            for segment in segments:
                words = segment.words
                if not words:
                    continue

                # Group words into short 3-4 word punchy bursts
                chunk_size = 4
                for i in range(0, len(words), chunk_size):
                    chunk = words[i:i + chunk_size]
                    if not chunk:
                        continue
                    start_str = self._format_timestamp(chunk[0].start)
                    end_str = self._format_timestamp(chunk[-1].end)
                    text = " ".join([w.word.strip().upper() for w in chunk])
                    if text:
                        ass_content.append(
                            f"Dialogue: 0,{start_str},{end_str},YellowShorts,,0,0,0,,{text}"
                        )
                        dialogue_count += 1

            if dialogue_count == 0:
                print("[Subtitles] No speech detected in clip.")
                return False

            with open(ass_output_path, "w", encoding="utf-8") as f:
                f.write("\n".join(ass_content))

            print(f"[Subtitles] Generated {dialogue_count} subtitle bursts in yellow bold style.")
            return True

        except Exception as e:
            print(f"[Subtitles] Error generating subtitles: {e}")
            return False
        finally:
            try:
                audio_temp.unlink()
            except Exception:
                pass
