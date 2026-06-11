# 🚁 RAVEN System (Rapid Autonomous Victim Emergency Network)

![Status](https://img.shields.io/badge/Status-Hackathon_Ready-success)
![License](https://img.shields.io/badge/License-MIT-blue)
![Python](https://img.shields.io/badge/Python-3.10+-yellow)

**RAVEN** is a next-generation, fully autonomous AI drone surveillance and emergency response system. Designed to dramatically reduce emergency response times, RAVEN utilizes edge-deployed computer vision and advanced Vision-Language Models (VLMs) to detect, verify, and broadcast severe vehicular collisions in real-time.

## 🌟 Key Features

- **Multi-Agent Verification Pipeline:** Utilizes a fine-tuned YOLOv8 model for real-time bounding box detection, cross-verified by a Moondream VLM to guarantee zero false positives on standing traffic.
- **Autonomous Emergency Dispatch:** Automatically assesses accident severity (Normal, Serious, Critical) and broadcasts live telemetry to the dashboard.
- **Live Command Center Dashboard:** A sleek, fully responsive HTML/JS command center featuring real-time WebSockets, OpenStreetMap integration, live video feeds, and an AI semantic analysis typewriter effect.
- **Text-to-Speech Status Updates:** Integrated Web Speech API provides hands-free, continuous audible situational awareness for operators.

## 🛠️ Technology Stack

- **Backend:** FastAPI, Python, SQLAlchemy, WebSockets
- **AI Models:** 
  - `YOLOv8` (Fine-tuned for collision and vehicle damage detection)
  - `Moondream` (Local VLM running via Ollama for semantic scene assessment)
- **Frontend:** Vanilla HTML5, CSS3, JavaScript
- **Mapping:** OpenStreetMap via Leaflet.js

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- [Ollama](https://ollama.ai/) installed locally
- Moondream model pulled (`ollama run moondream`)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/raven-system.git
   cd raven-system
   ```

2. **Install dependencies:**
   Ensure you are in the `backend` or `firmware` environment:
   ```bash
   pip install -r firmware/requirements.txt
   ```

3. **Ensure Models are Present:**
   Make sure your fine-tuned YOLO model is placed in `models/best.pt`.

### 🏃‍♂️ Running the System

You can run the entire system instantly using the provided batch script:
```bash
./run_demo.bat
```
This script will:
1. Boot up the FastAPI backend on `http://localhost:8000`
2. Automatically open the live Command Center Dashboard in your default web browser.

**Using the Dashboard:**
- Click **Start Analysis** to commence the live AI video feed processing.
- Click **Enable Audio** to unlock the text-to-speech incident broadcasts.

## 🤝 Contributing
Built during a Hackathon! Pull requests and ideas for further autonomous response integration are always welcome.

## 📄 License
This project is licensed under the MIT License.
