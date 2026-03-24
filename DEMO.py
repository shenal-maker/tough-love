"""
EmotiArm — HACKATHON DEMO
Shows all 3 emotional responses with full arm movements
"""

import os, time, threading, random
from dotenv import load_dotenv
load_dotenv()

import cyberwave as cw
from elevenlabs import ElevenLabs, play

# Connect
print("="*60)
print("EmotiArm — Emotional Support Robot Demo")
print("="*60)
print("\n1. Open: https://cyberwave.com/environments/f3016ce0-620b-466f-81bd-7d75e7bf46e0")
print("2. Click 'Simulate' button in Cyberwave UI")
print("3. Watch the robot arm respond to emotions!")
print("\nStarting demo in 5 seconds...")
time.sleep(5)

robot = cw.twin("the-robot-studio/so101", environment="f3016ce0-620b-466f-81bd-7d75e7bf46e0")
el = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

def move(pose, delay=0.4):
    for joint, angle in pose.items():
        robot.joints.set(joint, angle, source_type='sim')
    time.sleep(delay)

def speak(text):
    try:
        print(f"  🔊 Speaking: '{text}'")
        audio = el.text_to_speech.convert(
            text=text,
            voice_id="JBFqnCBsd6RMkjVDRZzb",
            model_id="eleven_turbo_v2_5",
            output_format="mp3_44100_128",
        )
        play(audio)
    except Exception as e:
        print(f"  [Voice Error: {e}]")

# Motion sequences
REST = {"1": 0, "2": 45, "3": -45, "4": 0, "5": 0, "6": 50}
PAT_SEQUENCE = [
    {"1": 0, "2": 60, "3": -30, "4": 30, "5": 0, "6": 50},
    {"1": 0, "2": 70, "3": -20, "4": 40, "5": 0, "6": 50},
    {"1": 0, "2": 65, "3": -25, "4": 35, "5": 0, "6": 50},
    {"1": 0, "2": 70, "3": -20, "4": 40, "5": 0, "6": 50},
]
WIPE_SEQUENCE = [
    {"1": 10, "2": 65, "3": -20, "4": 35, "5": 0, "6": 80},
    {"1": -10, "2": 65, "3": -20, "4": 35, "5": 0, "6": 80},
    {"1": 10, "2": 65, "3": -20, "4": 35, "5": 0, "6": 80},
]
SLAP_SEQUENCE = [
    {"1": 0, "2": 80, "3": -10, "4": 50, "5": 0, "6": 50},
    {"1": 0, "2": 50, "3": -40, "4": 20, "5": 0, "6": 50},
    {"1": 0, "2": 80, "3": -10, "4": 50, "5": 0, "6": 50},
]

# Demo sequence - YC Style
print("\n" + "="*60)
print("THE PROBLEM: 83% of remote workers feel lonely.")
print("Productivity apps fail. Nobody's there when you struggle.")
print("="*60)
time.sleep(2)

print("\n" + "="*60)
print("THE SOLUTION: Physical AI that notices and responds.")
print("="*60)
time.sleep(2)

print("\n[SCENARIO 1] You're working late. You start crying.")
time.sleep(1)
print("→ EmotiArm detects: mouth down, head tilted")
time.sleep(1)
speak("Hey. I'm here. You're going to be okay.")
print("→ Gentle patting motion...")
for pose in PAT_SEQUENCE:
    move(pose, 0.4)
print("→ Wipes your tears...")
for pose in WIPE_SEQUENCE:
    move(pose, 0.35)
move(REST, 0.5)
time.sleep(3)

print("\n[SCENARIO 2] You lose focus. Check your phone.")
time.sleep(1)
print("→ EmotiArm detects: face turned away >3 seconds")
time.sleep(1)
print("→ SLAP!")
for pose in SLAP_SEQUENCE:
    move(pose, 0.2)
speak("Focus! Eyes on the screen!")
move(REST, 0.5)
time.sleep(3)

print("\n" + "="*60)
print("HOW IT WORKS:")
print("="*60)
print("• MediaPipe: 468 facial landmarks, 10Hz detection")
print("• Cyberwave: SO-101 digital twin, cloud robot control")
print("• ElevenLabs: Natural voice synthesis")
print("• Built in 6 hours for this hackathon")
time.sleep(2)

print("\n" + "="*60)
print("THE VISION:")
print("="*60)
print("Start: Remote workers ($50 desk companion)")
print("Next: Therapy offices, hospitals, elderly care")
print("Future: Physical AI that feels like companionship")
print("="*60)
print("\nQuestions?")
