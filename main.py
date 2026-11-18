"""
Live Stream Auto-Clipper & Shorts Generator
Automates real-time clipping from active livestreams without waiting for the stream to end.
"""
import sys
import time
import threading
import argparse
from pathlib import Path

from config import DEFAULT_CLIP_DURATION, DEFAULT_LAYOUT, OUTPUT_DIR
from buffer_manager import StreamBufferManager
from shorts_formatter import ShortsFormatter
from chat_watcher import LiveChatWatcher
from uploader import YouTubeShortsUploader

class LiveClipperApp:
    def __init__(self, stream_url: str, clip_duration: int = DEFAULT_CLIP_DURATION, layout: str = DEFAULT_LAYOUT):
        self.stream_url = stream_url
        self.clip_duration = clip_duration
        self.layout = layout
        self.buffer_manager = StreamBufferManager(stream_url)
        self.formatter = ShortsFormatter()
        self.uploader = YouTubeShortsUploader()
        self.chat_watcher = None

    def on_trigger(self, trigger_reason: str = "Manual Trigger"):
        """Launches clip processing in a background thread so the stream never stops buffering."""
        thread = threading.Thread(target=self._process_clip, args=(trigger_reason,), daemon=True)
        thread.start()

    def _process_clip(self, trigger_reason: str):
        print(f"\n==================================================")
        print(f"🎬 TRIGGER EVENT: {trigger_reason}")
        print(f"==================================================")
        timestamp = int(time.time())
        raw_clip_path = OUTPUT_DIR / f"raw_clip_{timestamp}.ts"

        # 1. Extract recent segments from rolling buffer (Instant < 0.5s)
        success = self.buffer_manager.extract_clip(raw_clip_path, self.clip_duration)
        if not success:
            print("⚠️ Could not extract clip (stream may have just started). Try again in 10-15 seconds.")
            return

        # 2. Format to 9:16 Vertical Video in background (FFmpeg)
        short_path = self.formatter.format_to_short(
            raw_clip_path,
            title_tag="GTA 6 HIGHLIGHT",
            layout=self.layout
        )

        if short_path:
            # 3. Prepare Upload / Metadata
            self.uploader.upload_short(
                short_path,
                title="INSANE GTA 6 MOMENT",
                streamer_name="Streamer",
                stream_url=self.stream_url
            )
            print(f"✨ Ready-to-Post Short created: {short_path.name}")
            print(f"[LiveClipper] Continuing to monitor stream in real time... (Press [Enter] for next clip)\n")

    def run(self):
        print("""
=====================================================
🎮 LIVE STREAM REAL-TIME AUTO-CLIPPER FOR SHORTS
=====================================================
Target Stream: {url}
Clip Length:   {dur}s
Shorts Layout: {lay}
=====================================================
Controls:
  [Enter] or 'c' -> Instantly Clip & Format last {dur}s
  'q'           -> Quit
=====================================================
""".format(url=self.stream_url, dur=self.clip_duration, lay=self.layout))

        # 1. Start rolling buffer
        self.buffer_manager.start_recording()

        # 2. If YouTube stream, hook up live chat watcher
        if "youtube.com" in self.stream_url or "youtu.be" in self.stream_url:
            self.chat_watcher = LiveChatWatcher(self.stream_url, self.on_trigger)
            self.chat_watcher.start()

        print("[*] Stream buffer warming up... In ~15 seconds you can take your first clip!")

        try:
            while True:
                user_input = input("\n[LiveClipper] Press [Enter] to CLIP NOW, or 'q' to quit: ").strip().lower()
                if user_input == 'q':
                    break
                else:
                    self.on_trigger("Manual User Trigger")
        except KeyboardInterrupt:
            pass
        finally:
            self.shutdown()

    def shutdown(self):
        print("\n[LiveClipper] Shutting down...")
        if self.chat_watcher:
            self.chat_watcher.stop()
        self.buffer_manager.stop_recording()
        print("[LiveClipper] Done.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Real-Time Live Stream Clipper")
    parser.add_argument("--url", type=str, help="Live stream URL (YouTube or Twitch)")
    parser.add_argument("--duration", type=int, default=DEFAULT_CLIP_DURATION, help="Clip length in seconds")
    parser.add_argument("--layout", type=str, default=DEFAULT_LAYOUT, choices=["blur_fill", "split_cam_top", "center_crop"])

    args = parser.parse_args()

    target_url = args.url
    if not target_url:
        target_url = input("Enter YouTube or Twitch Live Stream URL: ").strip()

    app = LiveClipperApp(target_url, clip_duration=args.duration, layout=args.layout)
    app.run()
