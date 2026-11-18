"""
AI Enhancer (Custom-Tuned for CarryMinati & GamerFleet):
Uses Gemini AI to evaluate clips and generate viral titles tailored specifically to
CarryisLive and GamerFleet's unique streaming personas, humor, and audience memes.
"""
import os
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

class AIEnhancer:
    def __init__(self, api_key: str = GEMINI_API_KEY):
        self.api_key = api_key
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent?key={self.api_key}"

    def analyze_clip(self, transcript: str, streamer_name: str = "CarryisLive", game: str = "GTA 6") -> dict:
        """
        Generates hyper-targeted viral titles specifically tailored for CarryMinati or GamerFleet.
        """
        if not self.api_key:
            return self._fallback(streamer_name, game)

        if not transcript or len(transcript.strip()) < 5:
            transcript = "Intense gaming moment, funny reactions, screaming and banter."

        # Specific Persona Prompts for Streamers
        if "speed" in streamer_name.lower():
            persona_guidelines = (
                "You are writing a title and SEO tags for ISHOWSPEED (Speed). "
                "Speed's audience loves: EXTREME CRASHOUTS, BARKING, LOUD SCREAMING, "
                "CRISTIANO RONALDO / SEWEY MOMENTS, UNHINGED REACTIONS, BACKFLIPS, AND PURE CHAOS. "
                "Use high-energy all-caps viral hooks with emojis like 💀, 😭, 😱, 🔥, ⚡. "
                "Examples: 'SPEED COMPLETELY LOST HIS MIND 💀😭 #shorts #ishowspeed', "
                "'SPEED'S CRAZIEST CRASHOUT EVER 😱 #shorts #speed', "
                "'SPEED COULD NOT BELIEVE WHAT HAPPENED 💀⚡ #shorts #ishowspeed'."
            )
        elif "carry" in streamer_name.lower():
            persona_guidelines = (
                "You are writing a title for CARRYMINATI (CarryisLive). "
                "Carry's audience loves: UNFILTERED RAGE, DESK SLAMS, SCREAMING AT NOOBS, "
                "SAVAGE HINDI/ENGLISH ROASTS, and hilarious angry reactions. "
                "Use high-energy all-caps hooks with emojis like 💀, 😭, 💥, 😱. "
                "Examples: 'CARRY LOST HIS MIND AT THIS NOOB 💀💥 #shorts', 'CARRY'S BIGGEST DESK SLAM MOMENT 😭 #shorts', "
                "'CARRY BROKE HIS MIC AFTER THIS FAIL 💀 #shorts'."
            )
        else: # GamerFleet
            persona_guidelines = (
                "You are writing a title for GAMERFLEET (Anshu Bisht). "
                "Fleet's audience loves: WHOLESOME COMEDY, FUNNY LAUGHTER ATTACKS, CLUMSY FAILS, "
                "CLUTCH TURNING INTO CHOKE, and trolling his friends. "
                "Use punchy Hinglish/English hooks with emojis like 🤣, 💀, 😭, 🔥. "
                "Examples: 'FLEET BHAI YE KYA HO GAYA 🤣 #shorts', 'GAMERFLEET CLUTCH YA CHOKE? 💀 #shorts', "
                "'FLEET'S MOST EMBARRASSING MOMENT EVER 😭 #shorts'."
            )

        prompt = f"""
{persona_guidelines}

Target Creator: {streamer_name}
Game: {game}
Clip Transcript / Dialogue:
\"\"\"{transcript}\"\"\"

Analyze this moment and respond ONLY with a raw JSON object:
{{
  "title": "CATCHY ALL-CAPS VIRAL TITLE WITH EMOJIS AND #shorts",
  "virality_score": 9.2,
  "reaction_category": "Rage / Desk Slam / Clutch / Funny Fail / Troll",
  "reason": "1-sentence explanation of why this moment will blow up on Shorts",
  "hashtags": ["#shorts", "#{streamer_name.lower()}", "#gaming", "#{game.lower().replace(' ', '')}"]
}}
Do NOT use markdown code fences. Output valid JSON only.
"""

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.75,
                "responseMimeType": "application/json"
            }
        }

        try:
            resp = requests.post(self.api_url, json=payload, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                result = json.loads(text)
                print(f"\n[AIEnhancer - {streamer_name} Tuned] Analysis Complete:")
                print(f"  🔥 Virality Score: {result.get('virality_score', 'N/A')}/10 ({result.get('reaction_category', '')})")
                print(f"  ✨ AI Title:       {result.get('title', '')}")
                print(f"  💡 Reason:         {result.get('reason', '')}\n")
                return result
            else:
                return self._fallback(streamer_name, game)
        except Exception as e:
            return self._fallback(streamer_name, game)

    def _fallback(self, streamer_name: str, game: str) -> dict:
        if "speed" in streamer_name.lower():
            title = f"SPEED COMPLETELY LOST HIS MIND 💀😭 #shorts #ishowspeed"
            hashtags = ["#shorts", "#ishowspeed", "#speed", "#gaming", "#highlights"]
        elif "carry" in streamer_name.lower():
            title = f"CARRY LOST HIS MIND IN {game.upper()} 💀💥 #shorts #carryislive"
            hashtags = ["#shorts", "#carryislive", "#carryminati", "#gaming"]
        else:
            title = f"FLEET BHAI NE YE KYA KIYA?! 🤣 #shorts #gamerfleet"
            hashtags = ["#shorts", "#gamerfleet", "#fleet", "#gaming"]

        return {
            "title": title,
            "virality_score": 8.5,
            "reaction_category": "Gaming Highlight",
            "reason": "High-energy reaction moment from live stream",
            "hashtags": hashtags
        }
