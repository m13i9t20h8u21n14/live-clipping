"""
Chat Watcher: Monitors live YouTube chat in real-time using pytchat.
Detects message velocity spikes and viral reaction keywords without using Google API quota.
"""
import time
import re
import threading
from typing import Callable
from config import CHAT_WINDOW_SECONDS, SPIKE_MULTIPLIER, TRIGGER_KEYWORDS, COOLDOWN_SECONDS

class LiveChatWatcher:
    def __init__(self, video_id_or_url: str, on_spike_callback: Callable):
        self.stream_id = self._extract_video_id(video_id_or_url)
        self.on_spike_callback = on_spike_callback
        self.is_running = False
        self.thread = None
        self.last_clip_time = 0
        self.history_rates = []

    def _extract_video_id(self, url_or_id: str) -> str:
        # Check standard 11-character video ID regex
        match = re.search(r"(?:v=|\/live\/|youtu\.be\/)([a-zA-Z0-9_-]{11})", url_or_id)
        if match:
            return match.group(1)
        
        # If it's a channel live URL like @GamerFleet/live, resolve active video ID with yt-dlp
        if "@" in url_or_id or "/channel/" in url_or_id or "/c/" in url_or_id:
            try:
                import yt_dlp
                ydl = yt_dlp.YoutubeDL({'quiet': True, 'noplaylist': True})
                info = ydl.extract_info(url_or_id, download=False)
                resolved_id = info.get('id')
                if resolved_id:
                    print(f"[ChatWatcher] Resolved live video ID: {resolved_id}")
                    return resolved_id
            except Exception as e:
                print(f"[ChatWatcher] Could not resolve live video ID: {e}")

        return url_or_id

    def start(self):
        """Starts chat listening thread."""
        try:
            import pytchat
        except ImportError:
            print("[ChatWatcher] pytchat is not installed.")
            return

        self.is_running = True
        self.thread = threading.Thread(target=self._run_listener, daemon=True)
        self.thread.start()
        print(f"[ChatWatcher] Monitoring live chat for video: {self.stream_id}")

    def stop(self):
        self.is_running = False

    def _run_listener(self):
        import pytchat
        try:
            chat = pytchat.create(video_id=self.stream_id)
        except Exception as e:
            print(f"[ChatWatcher] Error connecting to chat: {e}")
            return

        window_start = time.time()
        msg_count = 0
        keyword_hits = 0

        while self.is_running and chat.is_alive():
            try:
                for c in chat.get().sync_items():
                    msg_count += 1
                    text_lower = c.message.lower()
                    for kw in TRIGGER_KEYWORDS:
                        if kw in text_lower:
                            keyword_hits += 1
                            break

                now = time.time()
                elapsed = now - window_start
                if elapsed >= CHAT_WINDOW_SECONDS:
                    mps = msg_count / elapsed  # Messages per second
                    self._evaluate_spike(mps, keyword_hits)

                    # Update history
                    self.history_rates.append(mps)
                    if len(self.history_rates) > 20:
                        self.history_rates.pop(0)

                    # Reset window
                    window_start = now
                    msg_count = 0
                    keyword_hits = 0

                time.sleep(1)
            except Exception as e:
                time.sleep(2)

    def _evaluate_spike(self, current_mps: float, keyword_hits: int):
        if not self.history_rates:
            return

        avg_mps = sum(self.history_rates) / len(self.history_rates)
        now = time.time()

        if now - self.last_clip_time < COOLDOWN_SECONDS:
            return  # Still in cooldown

        # Trigger condition: MPS spike > threshold OR high concentration of keywords
        is_spike = (avg_mps > 1.0 and current_mps > avg_mps * SPIKE_MULTIPLIER)
        is_keyword_rush = keyword_hits >= 5

        if is_spike or is_keyword_rush:
            print(f"\n[🔥 CHAT SPIKE DETECTED] MPS: {current_mps:.1f} (avg: {avg_mps:.1f}) | Keywords: {keyword_hits}")
            self.last_clip_time = now
            if self.on_spike_callback:
                self.on_spike_callback("Chat Velocity Spike")
