"""
EmotiArm — demo mode (keyboard-controlled, no webcam required)

Controls:
  s = SAD   → arm pats + comforts
  d = DISTRACTED → arm slaps + yells focus
  n = NEUTRAL    → arm rests
  q = quit
"""

import os, time, threading, random
from dotenv import load_dotenv

load_dotenv()

# ── Cyberwave ──────────────────────────────────────────────────────────────────
import cyberwave as cw
robot = cw.twin("the-robot-studio/so101")

def move(pose, delay=0.4):
    for joint, angle in pose.items():
        robot.joints.set(joint, angle)
    time.sleep(delay)

REST         = {"1": 0,   "2": 45, "3": -45, "4": 0,  "5": 0, "6": 50}
PAT_SEQUENCE = [
    {"1": 0, "2": 60, "3": -30, "4": 30, "5": 0, "6": 50},
    {"1": 0, "2": 70, "3": -20, "4": 40, "5": 0, "6": 50},
    {"1": 0, "2": 65, "3": -25, "4": 35, "5": 0, "6": 50},
    {"1": 0, "2": 70, "3": -20, "4": 40, "5": 0, "6": 50},
    {"1": 0, "2": 65, "3": -25, "4": 35, "5": 0, "6": 50},
]
WIPE_SEQUENCE = [
    {"1": 10,  "2": 65, "3": -20, "4": 35, "5": 0, "6": 80},
    {"1": -10, "2": 65, "3": -20, "4": 35, "5": 0, "6": 80},
    {"1": 10,  "2": 65, "3": -20, "4": 35, "5": 0, "6": 80},
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
from elevenlabs.client import ElevenLabs
from elevenlabs import play as el_play

el = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

SAD_LINES = [
    "Hey. I'm here. You're going to be okay.",
    "Take a breath. I've got you.",
    "It's alright to feel this way. I'm not going anywhere.",
]
DISTRACTED_LINES = [
    "Focus! Eyes on the screen!",
    "Hey! Back to work!",
    "I saw that. Get back to it.",
]

def speak(text):
    audio = el.text_to_speech.convert(
        text=text,
        voice_id="JBFqnCBsd6RMkjVDRZzb",
        model_id="eleven_v3",
        output_format="mp3_44100_128",
    )
    el_play(audio)

def speak_bg(text):
    threading.Thread(target=speak, args=(text,), daemon=True).start()

# ── State handlers ─────────────────────────────────────────────────────────────
def on_sad():
    print("[SAD] Comforting...")
    speak_bg(random.choice(SAD_LINES))
    play_motion(PAT_SEQUENCE, delay=0.4)
    play_motion(WIPE_SEQUENCE, delay=0.35)

def on_distracted():
    print("[DISTRACTED] Snapping to attention...")
    play_motion(SLAP_SEQUENCE, delay=0.2)
    speak_bg(random.choice(DISTRACTED_LINES))

def on_neutral():
    print("[NEUTRAL] Resting...")
    move(REST, 0.5)

# ── Main ───────────────────────────────────────────────────────────────────────
COOLDOWN = 5  # seconds between same-state triggers
last_state = None
last_trigger = 0

print("EmotiArm ready. Press s=sad  d=distracted  n=neutral  q=quit")
move(REST, 0.5)

import sys, tty, termios

def getch():
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        return sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)

while True:
    key = getch()
    now = time.time()

    if key == 'q':
        print("Bye!")
        break

    state = {'s': 'SAD', 'd': 'DISTRACTED', 'n': 'NEUTRAL'}.get(key)
    if not state:
        continue

    if state == last_state and (now - last_trigger) < COOLDOWN:
        print(f"[cooldown] {COOLDOWN - int(now - last_trigger)}s left")
        continue

    last_state = state
    last_trigger = now

    if state == 'SAD':
        on_sad()
    elif state == 'DISTRACTED':
        on_distracted()
    else:
        on_neutral()
