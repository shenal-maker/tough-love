# EmotiArm — Emotionally Intelligent Robot Companion

**Robotic Agents Hackathon 2026 | Cyberwave + ElevenLabs Tracks**

EmotiArm is an emotionally responsive robotic arm that detects your emotional state through facial recognition and responds with physical comfort or accountability. When you're sad, it pats your head and speaks words of comfort. When you're distracted, it slaps you back to focus.

## 🎯 The Problem

People working alone lack physical feedback for emotional regulation and accountability. Digital notifications are easy to ignore, but a physical robotic companion creates real-world presence and connection.

## 💡 The Solution

EmotiArm uses:
- **MediaPipe Face Mesh** (468 facial landmarks) to detect emotional states in real-time
- **Cyberwave Digital Twin** to control a SO-101 6-axis robotic arm via cloud API
- **ElevenLabs Text-to-Speech** for empathetic voice responses

## 🎬 Demo

The system detects three states:

### 😢 SAD
**Detection:** Mouth corners down, head tilted, prolonged face coverage  
**Response:** Gentle patting motion + comforting voice
- *"Hey. I'm here. You're going to be okay."*
- *"Take a breath. I've got you."*

### 😵 DISTRACTED  
**Detection:** Face turned away, looking off-center for 3+ seconds  
**Response:** Quick slap motion + accountability voice
- *"Focus! Eyes on the screen!"*
- *"Hey! Back to work!"*

### 😌 NEUTRAL
**Detection:** Face centered, normal expression  
**Response:** Arm returns to rest position

## 🏗️ Architecture

```
[Webcam] → [MediaPipe Face Mesh] → [State Classifier] → [Motion + Voice]
                                                            ↓         ↓
                                                    [Cyberwave]  [ElevenLabs]
                                                    (SO-101 arm) (TTS audio)
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Cyberwave account with SO-101 environment setup
- ElevenLabs API key

### Installation

```bash
# Clone the repository
git clone https://github.com/shenal-maker/tough-love.git
cd tough-love

# Install dependencies
pip install -r requirements.txt

# Create .env file
echo "CYBERWAVE_API_KEY=your-key-here" >> .env
echo "ELEVENLABS_API_KEY=your-key-here" >> .env
```

### Run

**Webcam Mode (automatic detection):**
```bash
python3 main.py
```

**Keyboard Demo Mode (manual triggers):**
```bash
python3 main_keyboard.py
# Press: s=sad, d=distracted, n=neutral, q=quit
```

## 🛠️ Tech Stack

- **Python 3.11** - Core runtime
- **Cyberwave SDK** - Digital twin control for SO-101 robotic arm
- **ElevenLabs API** - Natural text-to-speech voice synthesis
- **MediaPipe** - Real-time face mesh detection (468 landmarks)
- **OpenCV** - Webcam capture and video processing

## 📁 Project Structure

```
tough-love/
├── main.py              # Webcam-based emotion detection (full version)
├── main_keyboard.py     # Keyboard demo mode (fallback)
├── main_webcam.py       # Backup of webcam version
├── requirements.txt     # Python dependencies
├── .env                 # API keys (not in repo)
├── .gitignore          # Git ignore file
└── README.md           # This file
```

## 🎨 Motion Sequences

All motions are defined as keyframe sequences with joint angles in degrees:

- **REST**: Neutral home position
- **PAT_SEQUENCE**: Gentle head-patting motion (5 keyframes)
- **WIPE_SEQUENCE**: Tear-wiping across cheek (3 keyframes)
- **SLAP_SEQUENCE**: Quick forehead tap for focus (3 keyframes)

Each motion is executed on the Cyberwave digital twin in real-time.

## 🏆 Hackathon Tracks

**Cyberwave Track:** Digital twin simulation of SO-101 robotic arm with real-time joint control via cloud API

**ElevenLabs Track:** Dynamic voice synthesis with emotional context and multiple voice lines per state

## 🔮 Future Improvements

- Add emotion intensity detection (slight frown vs. crying)
- Multi-user support with face recognition
- Custom motion sequences via UI
- Integration with productivity apps (Slack, Calendar)
- Physical deployment on real SO-101 hardware

## 👥 Team

Built for the Robotic Agents Hackathon, March 13, 2026

## 📄 License

MIT License - Built during hackathon

## 🙏 Acknowledgments

- **Cyberwave** for the digital twin platform and SO-101 simulation
- **ElevenLabs** for high-quality voice synthesis
- **Google MediaPipe** for facial landmark detection
