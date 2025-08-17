# Chess-Robot: A Dual-Process Embodied Testbed for Cognitive Evaluation

A chess-playing robot that operationalizes **dual-process theory** for embodied AI:

- **System 1 (fast, intuitive, automatic):**  
  Perceive board → convert to FEN → pick the next move with Stockfish → execute precisely with a Kinova arm.

- **System 2 (slow, deliberative, analytical):**  
  Conversational reasoning about strategy via CoSMIC with a chess-specialized LLM, using shared game memory (speech in/out).

---

## 🎯 Project Goals
1. **Dataset creation** (perception ↔ action ↔ dialog traces) for training robotic foundation models in the chess domain.  
2. **Testbed for cognitive evaluation** of embodied systems (traditional vs. end-to-end).

Repo: [BuddhiGamage/chess_robot](https://github.com/BuddhiGamage/chess_robot)

---

## ✨ Key Features
- ArUco-based pose & piece detection with a single overhead camera.
- Board calibration from 4 manually annotated corners → homogeneous transform → 64 square coordinates.
- State extraction to FEN → Stockfish selects the next move.
- Kinova arm control for reliable pick-and-place and precise square targeting.
- **Dual-process architecture:**
  - *System 1:* reactive perception → reasoning → act loop (camera → ArUco → FEN → Stockfish → arm).  
  - *System 2:* CoSMIC-backed conversation about the game (speech→text, text→speech) using shared memory from System 1.
- Logging of board states, moves, and dialog to build an open dataset for robotic foundation models (e.g., OpenVLA).

---

## 🧭 Repository Layout (high-level)
```
aruco/ # ArUco marker helpers
chess/ # Chess/FEN helpers
chess_board/ # Board processing & calibration
move_kinova/ # Arm motion utilities
ocr/, tessdata/ # OCR utilities (if used)
photos/, qr_codes/ # Assets
simple_marker/ # Marker experiments
test/ # Quick tests / scripts

arm.py # Kinova control entry points
move.py, pick_and_place.py, move_to_x_y.py # Motion primitives
fen.py, return_fen.py # FEN conversion utilities
game.py, return_move.py# Game loop/next-move helpers
utilities.py # Common helpers
readme.md # (this file)
requirments.txt # Python deps (note spelling)
```

# 🛠️ Hardware & Software

## Hardware
- Kinova robotic arm (tested on author’s setup).
- Single RGB camera mounted above the board.
- Standard chessboard with **ArUco markers** for squares/pieces (as configured in this repo).

## Software
- **Python** (project scripts)  
- **Stockfish** chess engine  
- **Tesseract OCR** (if using OCR utilities)  
- **OpenCV** (with ArUco), NumPy, etc.

---

# 📦 Installation

### System packages (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install -y tesseract-ocr stockfish
```

### Python environment
```bash
python3 -m venv .venv
source .venv/bin/activate
# NOTE: the file in repo is spelled 'requirments.txt' currently:
pip install -r requirments.txt
```

If renamed to `requirements.txt`:
```bash
pip install -r requirements.txt
```

---

# 🚀 Quick Start (System 1)

1. **Print/attach ArUco markers** (see `aruco/` and `simple_marker/`) and mount a camera above the board.  
2. **Calibrate board**: click/select the 4 board corners once; the code computes the **homogeneous transform** and generates all 64 square coordinates.  
3. **Run the game loop (example):**
```bash
python3 game.py
# or, depending on your setup:
python3 return_move.py
```

These scripts:  
- capture a frame → detect markers → compute current piece layout,  
- build **FEN** → call **Stockfish** for the next move,  
- execute the move via **Kinova** (`arm.py`, `move.py`, `pick_and_place.py`).  

---

# 🧠 System 2 (Conversational / Reasoning)

- **CoSMIC** (Cognitive System for Machine Intelligent Computing) hosts a chess-specialized LLM for domain-specific cognition and dialog.  
- Speech I/O: **OpenAI speech recognition** (ASR) and **Google TTS** for spoken interaction.  
- **Shared memory**: System 2 has access to the latest System 1 board state and moves, so answers are grounded in actual play.

Resources:  
- [CoSMIC GitHub](https://github.com/TheOpenSI/CoSMIC)  
- [CoSMIC Website](https://opensi.net/cosmic/)  
- [ACIS 2024 Paper](https://aisel.aisnet.org/cgi/viewcontent.cgi?article=1030&context=acis2024)

---

# 🧪 Data Logging & Dataset

The project logs:  
- timestamped **RGB frames** (optional),  
- detected **board states** (FEN),  
- **chosen moves** (from Stockfish or human),  
- **arm actions** (start/goal 2D/3D, grasp/release events),  
- **dialog turns** (ASR text, LLM reply),  
- **metadata** (calibration parameters, homography, engine settings).  

**Schema (example JSONL per game):**
```json
{
  "t": 1723872351.512,
  "frame_id": "000123.jpg",
  "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
  "move": "e2e4",
  "policy": "stockfish",
  "arm": {"src":[x,y,z], "dst":[x,y,z], "action":"pick|place"},
  "speech_in": "What should I play next?",
  "speech_out": "I recommend Nf3.",
  "notes": "post-grasp regrip"
}
```

This dataset is intended to support training **end-to-end robotic foundation models** (e.g., OpenVLA-style pipelines) from synchronized perception–action–language traces.

---

# 📐 Board Calibration Details

- User selects **4 corners** once (top-left, top-right, bottom-right, bottom-left).  
- Code builds a **homogeneous transform** / projective mapping from image pixels → board square frame.  
- All **64 square centers** are computed automatically; these coordinates drive motion targets for the arm.

---

# 🧩 Kinova Motion Primitives

- `move_to_x_y.py` – move end-effector to a square center.  
- `pick_and_place.py` – grasp piece at square A and place at square B.  
- `arm.py` / `move.py` – low-level utilities (home, lift, descend, open/close gripper).  

See `move_kinova/` and motion scripts in root.

---

# 🔍 Troubleshooting

- **Markers not detected** → check lighting, focus, and marker size; verify camera intrinsics if using fisheye (`fisheye.py`).  
- **FEN looks wrong** → re-run corner calibration; verify ArUco IDs ↔ piece mapping.  
- **Kinova misses squares** → confirm Z heights and gripper offsets; re-measure square centers after any camera/board move.  
- **Stockfish not found** → ensure it’s installed and on PATH (`stockfish` CLI).  

---

# 🗺️ Roadmap

- [ ] Finalize robust logging of all moves + dialog.  
- [ ] Release an initial dataset snapshot.  
- [ ] Train a first end-to-end baseline using the dataset.  
- [ ] Benchmark **traditional (System 1)** vs **end-to-end** models on cognitive metrics (perception, memory, attention, reasoning, anticipation) in the chess domain.  
- [ ] Add reproducible calibration GUI + config.

---


---

# 🔖 Badges (optional)

Add badges at the top once ready:

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)]()  
[![Stockfish](https://img.shields.io/badge/engine-Stockfish-brightgreen.svg)]()  
[![Kinova](https://img.shields.io/badge/hardware-Kinova-black.svg)]()
