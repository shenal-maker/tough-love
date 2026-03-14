"""
EmotiArm — Webcam-based emotional support robot arm

Detects face emotions via MediaPipe:
  SAD → arm pats + comforts
  DISTRACTED → arm slaps + yells focus
  NEUTRAL → arm rests
"""

import os, time, threading, random
import cv2
import mediapipe as mp
from dotenv import load_dotenv

load_dotenv()

# ── Cyberwave ──────────────────────────────────────────────────────────────────
import cyberwave as cw

robot = cw.twin("the-robot-studio/so101", environment="f3016ce0-620b-466f-81bd-7d75e7bf46e0")

def move(pose, delay=0.4):
    """Move robot joints to target pose"""
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
from elevenlabs import ElevenLabs, play

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
    try:
        audio = el.text_to_speech.convert(
            text=text,
            voice_id="JBFqnCBsd6RMkjVDRZzb",
            model_id="eleven_turbo_v2_5",  # Faster for real-time responses
            output_format="mp3_44100_128",
        )
        el_play(audio)
    except Exception as e:
        print(f"[Voice Error] {e}")

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

# ── Face Detection (MediaPipe) ─────────────────────────────────────────────────
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

def classify_face(frame):
    """Returns: SAD, DISTRACTED, or NEUTRAL"""
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb)
    
    if not results.multi_face_landmarks:
        return "DISTRACTED"  # No face = looking away
    
    landmarks = results.multi_face_landmarks[0].landmark
    h, w = frame.shape[:2]
    
    # Key points
    nose_tip = landmarks[1]
    left_mouth = landmarks[61]
    right_mouth = landmarks[291]
    forehead = landmarks[10]
    
    # Mouth corners vs nose (SAD detection)
    mouth_y_avg = (left_mouth.y + right_mouth.y) / 2
    mouth_droop = mouth_y_avg > nose_tip.y + 0.02  # mouth below nose = frown
    
    # Head tilt down (SAD detection)
    head_down = nose_tip.y > forehead.y + 0.15
    
    # Face centered (DISTRACTED detection)
    face_center_x = nose_tip.x
    off_center = abs(face_center_x - 0.5) > 0.2  # face turned away
    
    if mouth_droop or head_down:
        return "SAD"
    elif off_center:
        return "DISTRACTED"
    else:
        return "NEUTRAL"

# ── Main ───────────────────────────────────────────────────────────────────────
COOLDOWN = 5  # seconds between same-state triggers
last_state = None
last_trigger = 0
no_face_start = None

print("="*60)
print("EmotiArm — Emotionally Intelligent Robot Companion")
print("="*60)
print("Initializing webcam...")
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("\n❌ ERROR: Cannot open webcam!")
    print("\nTroubleshooting:")
    print("  1. Check System Settings → Privacy & Security → Camera")
    print("  2. Enable 'Terminal' or your terminal app")
    print("  3. Restart terminal and try again")
    print("\nOr use keyboard demo mode: python3 main_keyboard.py")
    exit(1)

print("✓ Webcam ready")
print("✓ Cyberwave connected")
print("✓ ElevenLabs ready")
print("\nStates detected:")
print("  😢 SAD        → Pat + comfort")
print("  😵 DISTRACTED → Slap + focus")
print("  😌 NEUTRAL    → Rest position")
print("\nPress 'q' in video window to quit")
print("="*60)
move(REST, 0.5)

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break
        
        now = time.time()
        state = classify_face(frame)
        
        # Track sustained face absence
        if state == "DISTRACTED":
            if no_face_start is None:
                no_face_start = now
            elif now - no_face_start < 3:
                state = "NEUTRAL"  # need 3s absence to trigger
        else:
            no_face_start = None
        
        # Cooldown check
        if state == last_state and (now - last_trigger) < COOLDOWN:
            pass  # skip
        elif state != last_state or (now - last_trigger) >= COOLDOWN:
            last_state = state
            last_trigger = now
            
            if state == 'SAD':
                print("[SAD detected] Comforting...")
                on_sad()
            elif state == 'DISTRACTED':
                print("[DISTRACTED detected] Refocusing...")
                on_distracted()
            elif state == 'NEUTRAL':
                on_neutral()
        
        # Show video feed with state
        cv2.putText(frame, f"State: {state}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.imshow('EmotiArm - Press Q to quit', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    cap.release()
    cv2.destroyAllWindows()
    face_mesh.close()
    print("EmotiArm stopped.")
