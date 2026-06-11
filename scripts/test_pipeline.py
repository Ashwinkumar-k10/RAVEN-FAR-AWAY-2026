import time
import os
from firmware.fsm_agent import RavenAgent

try:
    from ultralytics import YOLO
except ImportError:
    print("Error: ultralytics is not installed. Please install it using 'pip install ultralytics'.")
    YOLO = None

def run_simulation():
    print("==============================================")
    print("RAVEN AUTONOMOUS SYSTEM SIMULATION")
    print("==============================================")
    
    agent = RavenAgent()
    
    print("\n--- Phase 1: Patrol ---")
    print(f"Current State: {agent.state}")
    time.sleep(2)
    
    print("\n--- Phase 2: YOLOv8 Live Detection (Friend's Model) ---")
    
    if YOLO is None:
        return
        
    model_path = os.path.join("models", "best.pt")
    if not os.path.exists(model_path):
        print(f"Error: Model not found at {model_path}")
        return
        
    # Load the actual model
    try:
        model = YOLO(model_path)
    except Exception as e:
        print(f"Failed to load YOLO model: {e}")
        return
        
    img_path = os.path.join("dashboard", "accident_frame.jpg")
    if not os.path.exists(img_path):
        print(f"Error: Test image not found at {img_path}")
        return
        
    # Run inference
    results = model(img_path)
    
    if len(results) > 0 and len(results[0].boxes) > 0:
        # Get the first detected box
        conf = float(results[0].boxes.conf[0])
        class_id = int(results[0].boxes.cls[0])
        severity = model.names[class_id] # "moderate" or "severe"
        print(f"Detected: {severity} accident with confidence {conf:.2f}")
        
        print("\n--- Phase 3: FSM Confidence Gate (3-Frame Persistence) ---")
        # Simulate feeding video frames. The FSM needs 3 consecutive frames with confidence > 0.70
        for i in range(1, 5):
            print(f"Processing Frame {i}...")
            agent.on_detect(
                confidence=conf,
                victim_count=2,       
                posture='lying',      
                fire_smoke=True,      
                vehicle_damage=severity
            )
            print(f"Current State: {agent.state}")
            if agent.state != 'PATROL':
                # Triggered! FSM transitioned.
                break
            time.sleep(1)
            
    else:
        print("No accident detected by YOLOv8.")
        
    print("\n--- Phase 4: Final State ---")
    print(f"Current State: {agent.state}")

if __name__ == "__main__":
    run_simulation()
