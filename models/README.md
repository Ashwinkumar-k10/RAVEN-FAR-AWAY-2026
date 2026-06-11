\# RAVEN — Rapid Autonomous Victim Emergency Network

\*\*FAR AWAY 2026 | Theme: Agentic \& Autonomous Systems | Deadline: 14 June 2026\*\*



\## Problem

1,50,000+ road accident deaths annually in India. 50% preventable 

within the Golden Hour. Current systems depend on human reporting 

— RAVEN eliminates that dependency.



\## Solution

AI-powered autonomous drone first-responder that detects accidents,

assesses severity, provides voice guidance, deploys first-aid payload,

and dispatches emergency services — all within 90 seconds, zero human trigger.



\## ML Model

\- Model    : YOLOv8s fine-tuned

\- Dataset  : Accident Detection Dataset v1 (Roboflow, CC BY 4.0)

\- Classes  : moderate, severe (2-class severity classification)

\- Images   : 11,780 (9,758 train / 1,347 val)

\- mAP@50   : 0.978

\- Precision: 0.976

\- Recall   : 0.937



\## Repository Structure

/firmware   — Raspberry Pi Python FSM agent

/ml         — YOLOv8 weights + training scripts

/backend    — FastAPI server + WebSocket

/frontend   — React dashboard

/pcb        — KiCad schematic + Gerber files

/cad        — FreeCAD payload bay STL + STEP

/docs       — Architecture diagram, BOM, wiring

/demo       — Demo video link + screenshots

## Quick Start

```bash

pip install ultralytics opencv-python fastapi

python firmware/raven\_fsm.py

```



\## Team

TECHTONICS — CIT Chennai, Batch 2024



\## License

MIT License

