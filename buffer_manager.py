"""
Buffer Manager: Maintains a rolling buffer of an active live stream using Streamlink and FFmpeg.
Streams in real time without waiting for stream to finish. Works on both YouTube and Twitch.
"""
import os
import sys
import time
import subprocess
import threading
from pathlib import Path
import streamlink

from config import (
    BUFFER_DIR,
    SEGMENT_TIME_SECONDS,
    MAX_BUFFER_SEGMENTS,
    DEFAULT_CLIP_DURATION
)

class StreamBufferManager:
    def __init__(self, stream_url: str):
        self.stream_url = stream_url
        self.process = None
        self.fd = None
        self.is_running = False
        self._pipe_thread = None
        self._lock = threading.Lock()
        self._clean_buffer_dir()

    def _clean_buffer_dir(self):
        """Clears previous segments from buffer directory."""
        if BUFFER_DIR.exists():
            for f in BUFFER_DIR.glob("*.ts"):
                try:
                    f.unlink()
                except Exception:
                    pass
            for f in BUFFER_DIR.glob("*.txt"):
                try:
                    f.unlink()
                except Exception:
                    pass

    def start_recording(self):
        """Connects via Streamlink and pipes live stream into FFmpeg rolling buffer."""
        self.is_running = True
        pattern = (BUFFER_DIR / "seg_%04d.ts").as_posix()

        print(f"[BufferManager] Connecting to live stream: {self.stream_url}")
        session = streamlink.Streamlink()
        session.set_option("http-headers", {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"
        })
        
        streams = session.streams(self.stream_url)
        if not streams:
            raise ValueError(f"No active streams found for: {self.stream_url}")

        selected_stream = streams.get("720p60") or streams.get("720p") or streams.get("best")
        if not selected_stream:
            selected_stream = list(streams.values())[-1]

        self.fd = selected_stream.open()
        print(f"[BufferManager] Stream connection open ({selected_stream}). Starting FFmpeg buffer...")

        cmd = [
            "ffmpeg", "-hide_banner", "-loglevel", "error",
            "-i", "pipe:0",
            "-c", "copy",
            "-f", "segment",
            "-segment_time", str(SEGMENT_TIME_SECONDS),
            "-reset_timestamps", "1",
            "-y", pattern
        ]

        self.process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0
        )

        # Worker thread to continuously pump live bytes into FFmpeg stdin
        def _pump_data():
            while self.is_running and self.fd and self.process and self.process.poll() is None:
                try:
                    data = self.fd.read(65536)
                    if not data:
                        break
                    self.process.stdin.write(data)
                except Exception:
                    break

        self._pipe_thread = threading.Thread(target=_pump_data, daemon=True)
        self._pipe_thread.start()
        print(f"[BufferManager] Live buffer active! (Holding up to {MAX_BUFFER_SEGMENTS * SEGMENT_TIME_SECONDS}s)")

    def stop_recording(self):
        """Stops the recording cleanly."""
        self.is_running = False
        if self.fd:
            try:
                self.fd.close()
            except Exception:
                pass
        if self.process:
            try:
                if self.process.stdin:
                    self.process.stdin.close()
                if sys.platform == "win32":
                    subprocess.call(['taskkill', '/F', '/T', '/PID', str(self.process.pid)],
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                else:
                    self.process.terminate()
            except Exception as e:
                pass
        print("[BufferManager] Stream recording stopped.")

    def get_recent_segments(self, duration_seconds: int = DEFAULT_CLIP_DURATION):
        """
        Returns list of segment file paths covering the requested recent duration.
        Cleans up old segments exceeding the max rolling buffer window.
        """
        all_segments = [p for p in BUFFER_DIR.glob("seg_*.ts") if p.stat().st_size > 0]
        if not all_segments:
            return []

        all_segments.sort(key=lambda p: os.path.getmtime(p))

        # Circular buffer retention cleanup: remove chunks older than MAX_BUFFER_SEGMENTS
        if len(all_segments) > MAX_BUFFER_SEGMENTS + 10:
            excess = all_segments[:-MAX_BUFFER_SEGMENTS]
            for old_f in excess:
                try:
                    old_f.unlink()
                except Exception:
                    pass
            all_segments = all_segments[-MAX_BUFFER_SEGMENTS:]

        # Discard the very last segment (it is currently actively written)
        if len(all_segments) > 1:
            stable_segments = all_segments[:-1]
        else:
            stable_segments = all_segments

        needed_count = max(1, int(duration_seconds / SEGMENT_TIME_SECONDS))
        selected = stable_segments[-needed_count:]
        return selected

    def extract_clip(self, output_path: Path, duration_seconds: int = DEFAULT_CLIP_DURATION) -> bool:
        """
        Stitches the most recent segments into a single raw MP4/TS clip in < 0.5s.
        """
        with self._lock:
            segments = self.get_recent_segments(duration_seconds)
            if not segments:
                print("[BufferManager] No segments available yet. Please wait a few seconds.")
                return False

            actual_duration = len(segments) * SEGMENT_TIME_SECONDS
            print(f"[BufferManager] Stitching {len(segments)} segments (~{actual_duration}s)...")

            concat_list_path = BUFFER_DIR / f"concat_{int(time.time())}.txt"
            with open(concat_list_path, "w", encoding="utf-8") as f:
                for seg in segments:
                    safe_path = str(seg.resolve()).replace("\\", "/")
                    f.write(f"file '{safe_path}'\n")

            cmd = [
                "ffmpeg", "-hide_banner", "-loglevel", "error",
                "-f", "concat", "-safe", "0",
                "-i", str(concat_list_path),
                "-c", "copy",
                "-y", str(output_path)
            ]

            res = subprocess.run(cmd)
            try:
                concat_list_path.unlink()
            except Exception:
                pass

            if res.returncode == 0 and output_path.exists() and output_path.stat().st_size > 0:
                print(f"[BufferManager] Successfully extracted raw clip: {output_path.name}")
                return True
            else:
                print("[BufferManager] Failed to extract clip.")
                return False
