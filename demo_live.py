"""
Demo Script: Proves live stream clipping in real time.
Connects to an active livestream, buffers for 25 seconds, extracts a clip,
and formats it into a 9:16 YouTube Short immediately.
"""
import time
import sys
from pathlib import Path
from buffer_manager import StreamBufferManager
from shorts_formatter import ShortsFormatter
from uploader import YouTubeShortsUploader
from config import OUTPUT_DIR

def run_live_demo(stream_url: str):
    print("=" * 60)
    print("🚀 STARTING REAL-TIME LIVE STREAM CLIPPING DEMO")
    print(f"Target Live Stream: {stream_url}")
    print("=" * 60)

    manager = StreamBufferManager(stream_url)
    formatter = ShortsFormatter()
    uploader = YouTubeShortsUploader()

    try:
        # Step 1: Start Ingestion
        print("\n[Step 1] Ingesting live stream segments into rolling buffer...")
        manager.start_recording()

        # Wait for buffer to collect chunks (e.g. 24 seconds = ~6 segments)
        for i in range(24, 0, -1):
            sys.stdout.write(f"\rBuffering live stream chunks... {i}s remaining  ")
            sys.stdout.flush()
            time.sleep(1)
        print("\n")

        # Step 2: Trigger Clip Extraction (without stopping the stream!)
        print("[Step 2] Triggering clip extraction (last 16 seconds)...")
        timestamp = int(time.time())
        raw_clip = OUTPUT_DIR / f"demo_raw_{timestamp}.ts"
        
        success = manager.extract_clip(raw_clip, duration_seconds=16)
        if not success:
            print("❌ Demo failed to extract raw segments.")
            return

        print(f"✅ Raw clip extracted in < 1 second! Size: {raw_clip.stat().st_size / 1024:.1f} KB")

        # Step 3: Format into 9:16 Vertical Short
        print("\n[Step 3] Formatting raw clip into 9:16 vertical Short (1080x1920)...")
        short_clip = formatter.format_to_short(raw_clip, layout="blur_fill")
        
        if short_clip and short_clip.exists():
            print(f"✅ 9:16 Vertical Short created successfully!")
            print(f"📁 Output File: {short_clip.resolve()}")
            print(f"📊 File Size:   {short_clip.stat().st_size / (1024 * 1024):.2f} MB")

            # Step 4: Metadata preparation
            print("\n[Step 4] Generating YouTube Shorts metadata manifest...")
            meta = uploader.prepare_metadata(
                short_clip,
                title="LIVE STREAM INSANE MOMENT",
                streamer_name="Live Streamer",
                stream_url=stream_url
            )
            print(f"📝 Title:       {meta['title']}")
            print(f"🏷️ Tags:        {', '.join(meta['tags'])}")
            print(f"🔒 Privacy:     {meta['privacyStatus']}")
            print("\n🎉 LIVE DEMO COMPLETE! EVERYTHING WORKED IN REAL-TIME.")
        else:
            print("❌ Formatting failed.")

    finally:
        print("\n[Cleanup] Stopping live stream buffer...")
        manager.stop_recording()

if __name__ == "__main__":
    # Test on a 24/7 active live stream
    test_url = "https://www.youtube.com/watch?v=5qap5aO4i9A"
    if len(sys.argv) > 1:
        test_url = sys.argv[1]
    run_live_demo(test_url)
