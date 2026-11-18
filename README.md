# Real-Time Live Stream Clipper: CarryisLive & GamerFleet Edition

Automated clipping of **CarryMinati (CarryisLive)** and **GamerFleet** live streams in real time with **burned-in yellow bold subtitles** and **Gemini AI viral titles**.

---

## ⚡ Features
1. **1-Click Streamer Presets**: No need to search for links. Just specify `--streamer carry` or `--streamer fleet`.
2. **Zero-Wait Ingestion**: Buffers live stream chunks in real-time (`Streamlink` + `FFmpeg`) without waiting for the stream to end.
3. **Yellow Bold Subtitles**: Auto-generates high-contrast, slanted yellow subtitles with black outlines matching the Shorts format.
4. **Gemini 3.5 AI Integration**: Analyzes speech to score virality (1–10) and writes custom-tailored Carry & Fleet titles.
5. **Indian Gaming Chat Triggers**: Automatically clips when live chat explodes with `bhai`, `op`, `rage`, `desk`, `clutch`, `khatam`, or `lmao`.

---

## 🚀 Quick Start

### 1. Clip CarryMinati (CarryisLive)
```powershell
python main.py --streamer carry
```

### 2. Clip GamerFleet
```powershell
python main.py --streamer fleet
```

### 3. Or Clip Any Custom Live Stream
```powershell
python main.py --url "https://www.youtube.com/watch?v=<VIDEO_ID>"
```

### Controls in Terminal:
* Press **`[Enter]`** at any funny or rage moment to instantly extract and format the last 2 minutes (120s).
* Press **`q`** to quit cleanly.

All finished 9:16 Shorts with burned-in yellow subtitles and metadata are saved in `output_clips/`.
