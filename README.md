# Real-Time Live Stream Auto-Clipper (`clip-watcher`)

Clip highlights from active YouTube & Twitch livestreams (GTA 6, esports, IRL) in real time **without waiting for the stream to end**.

---

## ⚡ How It Works
1. **Zero-Wait Ingestion (`Streamlink` + `FFmpeg`)**: Connects to the active stream and writes rolling 4-second chunks (`.ts`) to a circular 3-minute memory/disk buffer.
2. **Instant Clip Extraction**: When a moment happens, it stitches the last 30–60 seconds in `< 0.5s` using FFmpeg's concat demuxer (lossless, no re-encoding).
3. **Shorts 9:16 Auto-Formatter**: Automatically formats the raw clip into **1080x1920** vertical video:
   - `blur_fill`: Blurred 9:16 background with sharp 16:9 gameplay centered.
   - `split_cam_top`: Facecam on top, gameplay on bottom.
   - `center_crop`: Direct 9:16 center crop.
4. **Auto-Trigger & SEO Metadata**: Listens to YouTube live chat velocity spikes (`pytchat`) or triggers on 1-click `[Enter]`, generating viral YouTube Shorts titles, tags, and descriptions.

---

## 🚀 Quick Start

### 1. Run Interactive Clipper on Any Stream
```powershell
python main.py --url "https://www.twitch.tv/<channel_name>" --duration 45
```
Or for YouTube:
```powershell
python main.py --url "https://www.youtube.com/watch?v=<video_id>" --duration 45
```

### 2. Controls in Terminal
* Press **`[Enter]`** or **`c`** at any moment to instantly extract and format the last 45 seconds into a Short.
* Press **`q`** to safely stop and clean up.

### 3. Check Outputs
All finished 9:16 Shorts and their YouTube metadata JSON files are saved in:
`output_clips/`
