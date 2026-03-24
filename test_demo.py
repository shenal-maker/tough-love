"""
EmotiArm — Quick Test Script
Tests all 3 states automatically
"""

import os, time, threading, random
from dotenv import load_dotenv

load_dotenv()

# ── Cyberwave ──────────────────────────────────────────────────────────────────
import cyberwave as cw

print("Connecting to Cyberwave...")
robot = cw.twin("the-robot-studio/so101", environment="f3016ce0-620b-466f-81bd-7d75e7bf46e0")
print("✓ Connected!")

def move(pose, delay=0.4):
    try:
        for joint, angle in pose.items():
            robot.joints.set(joint, angle, source_type='sim')
        time.sleep(delay)
    except Exception as e:
        print(f"[Robot Error] {e}")

REST         = {"1": 0,   "2": 45, "3": -45, "4": 0,  "5": 0, "6": 50}
PAT_SEQUENCE = [
    {"1": 0, "2": 60, "3": -30, "4": 30, "5": 0, "6": 50},
    {"1": 0, "2": 70, "3": -20, "4": 40, "5": 0, "6": 50},
    {"1": 0, "2": 65, "3": -25, "4": 35, "5": 0, "6": 50},
]
SLAP_SEQUENCE = [
    {"1": 0, "2": 80, "3": -10, "4": 50, "5": 0, "6": 50},
    {"1": 0, "2": 50, "3": -40, "4": 20, "5": 0, "6": 50},
    {"1": 0, "2": 80, "3": -10, "4": 50, "5": 0, "6": 50},
]

def play_motion(sequence, delay=0.4):
    for pose in sequence:
        move(pose, delay)
    move(REST, 0.5)

# ── ElevenLabs ────────────────────────────────────────────────────────────────
from elevenlabs import ElevenLabs, play

print("Connecting to ElevenLabs...")
el = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))
print("✓ Connected!")

def speak(text):
    try:
        print(f"Speaking: {text}")
        audio = el.text_to_speech.convert(
            text=text,
            voice_id="JBFqnCBsd6RMkjVDRZzb",
            model_id="eleven_turbo_v2_5",
            output_format="mp3_44100_128",
        )
        play(audio)
    except Exception as e:
        print(f"[Voice Error] {e}")

# ── Test ───────────────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("RUNNING AUTOMATED TEST")
print("="*60)

print("\n[1/3] Testing REST position...")
move(REST, 0.5)
time.sleep(2)

print("\n[2/3] Testing SAD state (pat motion + voice)...")
speak("Hey. I'm here. You're going to be okay.")
play_motion(PAT_SEQUENCE, delay=0.4)
time.sleep(2)

print("\n[3/3] Testing DISTRACTED state (slap motion + voice)...")
play_motion(SLAP_SEQUENCE, delay=0.2)
speak("Focus! Eyes on the screen!")
time.sleep(2)

print("\n[FINAL] Returning to REST...")
move(REST, 0.5)

print("\n" + "="*60)
print("✓ TEST COMPLETE!")
print("="*60)
print("\nCheck your Cyberwave browser - did the arm move?")
