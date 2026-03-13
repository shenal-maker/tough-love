import time
import random
import threading
import cv2
import mediapipe as mp
import cyberwave as cw
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs.play import play

load_dotenv()

# ─── Tunable constants ───────────────────────────────────────────────────────

COOLDOWN_SECONDS            = 5
NEUTRAL_SPEAK_INTERVAL      = 60    # seconds between idle encouragement
NO_FACE_DISTRACTED_SECS     = 3.0   # face absent this long → DISTRACTED
EYES_CLOSED_SAD_SECS        = 2.0   # eyes closed this long  → SAD
DETECTION_HZ                = 10
EAR_THRESHOLD               = 0.20  # eye-aspect-ratio below → closed
NOSE_SIDE_THRESHOLD         = 0.25  # |nose_x − 0.5| above  → looking away
MOUTH_SAG_THRESHOLD         = 0.08  # mouth_y − nose_y above → frown
HEAD_TILT_THRESHOLD         = 0.25  # nose_y − forehead_y above → head down

# ─── Joint keyframes ────────────────────────────────────────────────────────

REST = {"1": 0, "2": 45, "3": -45, "4": 0, "5": 0, "6": 50}

PAT_SEQUENCE = [
    {"1": 0, "2": 60, "3": -30, "4": 30, "5": 0, "6": 50},  # raise arm
    {"1": 0, "2": 70, "3": -20, "4": 40, "5": 0, "6": 50},  # extend
    {"1": 0, "2": 65, "3": -25, "4": 35, "5": 0, "6": 50},  # pat down
    {"1": 0, "2": 70, "3": -20, "4": 40, "5": 0, "6": 50},  # pat up
    {"1": 0, "2": 65, "3": -25, "4": 35, "5": 0, "6": 50},  # pat down
    {"1": 0, "2": 70, "3": -20, "4": 40, "5": 0, "6": 50},  # pat up
    {"1": 0, "2": 65, "3": -25, "4": 35, "5": 0, "6": 50},  # pat down
]

WIPE_SEQUENCE = [
    {"1": 10,  "2": 65, "3": -20, "4": 35, "5": 0, "6": 80},  # reach
    {"1": -10, "2": 65, "3": -20, "4": 35, "5": 0, "6": 80},  # sweep
    {"1": 10,  "2": 65, "3": -20, "4": 35, "5": 0, "6": 80},  # sweep back
]

SLAP_SEQUENCE = [
    {"1": 0, "2": 80, "3": -10, "4": 50, "5": 0, "6": 50},  # wind up high
    {"1": 0, "2": 50, "3": -40, "4": 20, "5": 0, "6": 50},  # slap down FAST
    {"1": 0, "2": 80, "3": -10, "4": 50, "5": 0, "6": 50},  # retract
]

# ─── Voice lines ─────────────────────────────────────────────────────────────

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
NEUTRAL_LINES = [
    "You're doing great. Keep going.",
]

# ─── MediaPipe eye landmarks ─────────────────────────────────────────────────
# 6-point eye contour (P0=left-corner, P3=right-corner, P1/P2/P4/P5=lids)
LEFT_EYE  = [362, 385, 387, 263, 373, 380]
RIGHT_EYE = [33,  160, 158, 133, 153, 144]


# ─── Helpers ─────────────────────────────────────────────────────────────────

def eye_aspect_ratio(lm, indices, w, h):
    pts = [(lm[i].x * w, lm[i].y * h) for i in indices]
    v1    = abs(pts[1][1] - pts[5][1])
    v2    = abs(pts[2][1] - pts[4][1])
    horiz = abs(pts[0][0] - pts[3][0])
    return (v1 + v2) / (2.0 * horiz) if horiz else 0.0


def classify_face(lm, no_face_secs, eyes_closed_secs):
    if lm is None:
        return "DISTRACTED" if no_face_secs >= NO_FACE_DISTRACTED_SECS else "NEUTRAL"

    nose_tip   = lm[1]
    forehead   = lm[10]
    mouth_left = lm[61]
    mouth_right= lm[291]

    # Turned away
    if abs(nose_tip.x - 0.5) > NOSE_SIDE_THRESHOLD:
        return "DISTRACTED"

    # Frown
    mouth_avg_y = (mouth_left.y + mouth_right.y) / 2
    if mouth_avg_y > nose_tip.y + MOUTH_SAG_THRESHOLD:
        return "SAD"

    # Head tilted down
    if nose_tip.y > forehead.y + HEAD_TILT_THRESHOLD:
        return "SAD"

    # Eyes closed a while
    if eyes_closed_secs >= EYES_CLOSED_SAD_SECS:
        return "SAD"

    return "NEUTRAL"


# ─── Robot controller ────────────────────────────────────────────────────────

class ArmController:
    def __init__(self, twin_id):
        self.robot    = cw.twin(twin_id)
        self._lock    = threading.Lock()
        self._thread  = None

    def _run_sequence(self, frames, delays):
        with self._lock:
            for frame, delay in zip(frames, delays):
                for joint_id, angle in frame.items():
                    self.robot.joints.set(joint_id, angle)
                time.sleep(delay)

    def _dispatch(self, frames, delays):
        t = threading.Thread(target=self._run_sequence, args=(frames, delays), daemon=True)
        t.start()
        self._thread = t

    def rest(self):
        self._dispatch([REST], [0.1])

    def sad_response(self):
        frames = PAT_SEQUENCE + WIPE_SEQUENCE + [REST]
        delays = [0.3] * len(PAT_SEQUENCE) + [0.3] * len(WIPE_SEQUENCE) + [0.1]
        self._dispatch(frames, delays)

    def distracted_response(self):
        # Slap frame 1 is fast; retract is slower
        frames = SLAP_SEQUENCE + [REST]
        delays = [0.25, 0.08, 0.25, 0.5]
        self._dispatch(frames, delays)


# ─── Voice controller ────────────────────────────────────────────────────────

class VoiceController:
    def __init__(self):
        self._el = ElevenLabs()  # reads ELEVENLABS_API_KEY from env

    def _say(self, text):
        try:
            audio = self._el.text_to_speech.convert(
                text=text,
                voice_id="JBFqnCBsd6RMkjVDRZzb",   # George — warm male voice
                model_id="eleven_v3",
                output_format="mp3_44100_128",
            )
            play(audio)
        except Exception as e:
            print(f"[voice] error: {e}")

    def say(self, text):
        threading.Thread(target=self._say, args=(text,), daemon=True).start()


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    print("[init] connecting to Cyberwave twin…")
    arm   = ArmController("the-robot-studio/so101")
    print("[init] Cyberwave OK")

    print("[init] connecting to ElevenLabs…")
    voice = VoiceController()
    print("[init] ElevenLabs OK")

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError("[cam] cannot open webcam — check camera permissions")

    mp_face  = mp.solutions.face_mesh
    mp_draw  = mp.solutions.drawing_utils
    mp_style = mp.solutions.drawing_styles

    STATE_COLORS = {
        "SAD":        (100, 100, 255),  # red-ish (BGR)
        "DISTRACTED": (50,  50,  255),  # bright red
        "NEUTRAL":    (100, 200, 100),  # green
    }

    last_state          = "NEUTRAL"
    last_action_time    = 0.0
    last_neutral_speak  = time.time()   # don't fire immediately on start
    no_face_start       = None
    eyes_closed_start   = None

    arm.rest()
    print("[ready] EmotiArm running — press Q to quit\n")

    with mp_face.FaceMesh(
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    ) as face_mesh:

        while True:
            ret, frame = cap.read()
            if not ret:
                time.sleep(0.05)
                continue

            h, w   = frame.shape[:2]
            rgb    = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = face_mesh.process(rgb)
            now    = time.time()
            lm     = None

            if result.multi_face_landmarks:
                no_face_start = None
                lm = result.multi_face_landmarks[0].landmark

                ear = (eye_aspect_ratio(lm, LEFT_EYE, w, h) +
                       eye_aspect_ratio(lm, RIGHT_EYE, w, h)) / 2
                if ear < EAR_THRESHOLD:
                    eyes_closed_start = eyes_closed_start or now
                else:
                    eyes_closed_start = None

                # Draw face mesh overlay
                mp_draw.draw_landmarks(
                    frame,
                    result.multi_face_landmarks[0],
                    mp_face.FACEMESH_CONTOURS,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=mp_style.get_default_face_mesh_contours_style(),
                )
            else:
                eyes_closed_start = None
                no_face_start = no_face_start or now

            no_face_secs     = (now - no_face_start)     if no_face_start     else 0.0
            eyes_closed_secs = (now - eyes_closed_start) if eyes_closed_start else 0.0

            state = classify_face(lm, no_face_secs, eyes_closed_secs)

            # ── HUD overlay ──
            color = STATE_COLORS[state]
            cv2.rectangle(frame, (0, 0), (w, 60), (0, 0, 0), -1)
            cv2.putText(frame, f"EmotiArm  |  {state}", (16, 42),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.1, color, 2)

            # Show timers when relevant
            if no_face_secs > 0:
                cv2.putText(frame, f"no-face: {no_face_secs:.1f}s", (w - 240, 42),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (180, 180, 180), 1)
            if eyes_closed_secs > 0:
                cv2.putText(frame, f"eyes-closed: {eyes_closed_secs:.1f}s", (w - 280, h - 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.65, (180, 180, 180), 1)

            cv2.imshow("EmotiArm — Webcam", frame)

            # ── State machine ──
            cooldown_ok = (now - last_action_time) >= COOLDOWN_SECONDS

            if state == "SAD" and (last_state != "SAD" or cooldown_ok):
                print(f"[state] SAD  (no_face={no_face_secs:.1f}s  eyes_closed={eyes_closed_secs:.1f}s)")
                last_action_time = now
                last_state       = "SAD"
                voice.say(random.choice(SAD_LINES))
                arm.sad_response()

            elif state == "DISTRACTED" and (last_state != "DISTRACTED" or cooldown_ok):
                print(f"[state] DISTRACTED  (no_face={no_face_secs:.1f}s)")
                last_action_time = now
                last_state       = "DISTRACTED"
                arm.distracted_response()
                voice.say(random.choice(DISTRACTED_LINES))

            elif state == "NEUTRAL":
                if last_state != "NEUTRAL":
                    print("[state] NEUTRAL — returning to rest")
                    last_state = "NEUTRAL"
                    arm.rest()
                if (now - last_neutral_speak) >= NEUTRAL_SPEAK_INTERVAL:
                    last_neutral_speak = now
                    voice.say(random.choice(NEUTRAL_LINES))

            if cv2.waitKey(1) & 0xFF == ord("q"):
                print("[quit] shutting down…")
                break

            time.sleep(1.0 / DETECTION_HZ)

    cap.release()
    cv2.destroyAllWindows()
    arm.rest()


if __name__ == "__main__":
    main()
