# pyrefly: ignore [missing-import]
from transitions import Machine
import logging
import time
import requests
from firmware.hardware_interface import HardwareInterface
from firmware.agentic_llm import AgenticLLM

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("RAVEN_FSM")

BACKEND_API_URL = "http://localhost:8000/api/incident"

class RavenAgent:
    states = ['PATROL', 'DETECT', 'ASSESS', 'COMMUNICATE', 'DEPLOY', 'DISPATCH', 'RELAY']

    def __init__(self):
        self.machine = Machine(model=self, states=RavenAgent.states, initial='PATROL')
        
        # State transitions based on doc
        self.machine.add_transition(trigger='on_detect', source='PATROL', dest='DETECT', conditions=['is_confident'])
        self.machine.add_transition(trigger='on_assess', source='DETECT', dest='ASSESS')
        self.machine.add_transition(trigger='on_communicate', source='ASSESS', dest='COMMUNICATE')
        self.machine.add_transition(trigger='on_deploy', source='COMMUNICATE', dest='DEPLOY')
        self.machine.add_transition(trigger='on_dispatch', source='DEPLOY', dest='DISPATCH')
        self.machine.add_transition(trigger='on_relay', source='DISPATCH', dest='RELAY')
        self.machine.add_transition(trigger='on_clear', source='RELAY', dest='PATROL')

        self.hardware = HardwareInterface(mock_mode=True)
        self.llm = AgenticLLM(model_name="mistral")
        
        # Incident state variables
        self.current_incident = {}
        self.consecutive_detections = 0

    def is_confident(self, confidence, **kwargs):
        if confidence > 0.70:
            self.consecutive_detections += 1
        else:
            self.consecutive_detections = 0
            
        if self.consecutive_detections >= 3:
            self.consecutive_detections = 0  # reset after detection
            return True
        return False

    # --- State Entry Callbacks ---
    def on_enter_DETECT(self, confidence, victim_count, posture, fire_smoke, vehicle_damage):
        logger.info(f"Entered DETECT State. Confidence: {confidence}")
        self.current_incident = {
            'victim_count': victim_count,
            'posture': posture,
            'fire_smoke': fire_smoke,
            'vehicle_damage': vehicle_damage,
            'gps': self.hardware.get_gps_location()
        }
        self.on_assess()

    def on_enter_ASSESS(self):
        logger.info("Entered ASSESS State.")
        inc = self.current_incident
        
        # Scoring logic
        v_score = min(inc['victim_count'] * 10, 100)
        p_score = 100 if inc['posture'] == 'lying' else 20
        f_score = 100 if inc['fire_smoke'] else 0
        d_score = 100 if inc['vehicle_damage'] == 'severe' else 30
        
        severity = (v_score * 0.40) + (p_score * 0.30) + (f_score * 0.20) + (d_score * 0.10)
        self.current_incident['severity'] = round(severity, 2)
        
        if severity <= 30:
            tier = 'Minor'
        elif severity <= 70:
            tier = 'Serious'
        else:
            tier = 'Critical'
            
        self.current_incident['tier'] = tier
        logger.info(f"Assessment Complete. Severity: {severity}, Tier: {tier}")
        
        # Generate semantic assessment using Moondream
        img_path = "f:/HACKATHONS/FAR AWAY/dashboard/accident_frame.jpg"
        assessment = self.llm.analyze_scene(img_path)
        self.current_incident['semantic_assessment'] = assessment
        
        self.on_communicate()

    def on_enter_COMMUNICATE(self):
        logger.info("Entered COMMUNICATE State.")
        inc = self.current_incident
        script = self.llm.generate_guidance(inc['severity'], inc['victim_count'], inc['tier'])
        audio_file = self.llm.text_to_speech(script)
        if audio_file:
            self.hardware.play_audio(audio_file)
        self.on_deploy()

    def on_enter_DEPLOY(self):
        logger.info("Entered DEPLOY State.")
        self.hardware.release_payload()
        self.on_dispatch()

    def on_enter_DISPATCH(self):
        logger.info("Entered DISPATCH State.")
        inc = self.current_incident
        
        payload = {
            "latitude": inc['gps']['latitude'],
            "longitude": inc['gps']['longitude'],
            "victim_count": inc['victim_count'],
            "severity_score": inc['severity'],
            "tier": inc['tier'],
            "semantic_assessment": inc.get('semantic_assessment', '')
        }
        
        # Send SMS
        sms_msg = f"RAVEN ALERT: {inc['tier']} incident at Lat: {inc['gps']['latitude']}, Lon: {inc['gps']['longitude']}. Victims: {inc['victim_count']}."
        self.hardware.send_sms("+1234567890", sms_msg)
        
        # POST to backend
        try:
            res = requests.post(BACKEND_API_URL, json=payload)
            if res.status_code == 200:
                logger.info("Successfully dispatched incident to backend dashboard.")
            else:
                logger.error(f"Backend returned error: {res.text}")
        except Exception as e:
            logger.error(f"Failed to reach backend: {e}")
            
        self.on_relay()

    def on_enter_RELAY(self):
        logger.info("Entered RELAY State. Loitering and streaming data...")
        # Stay here and share status every 5 seconds via Mistral
        # Simulating a 15-second wait before responders arrive
        for i in range(3):
            status = self.llm.generate_status_update(self.current_incident)
            logger.info(f"\n>>> MISTRAL LIVE STATUS: {status}\n")
            try:
                requests.post("http://localhost:8000/api/status_update", json={"message": status})
            except Exception as e:
                logger.error(f"Failed to push status to dashboard: {e}")
            time.sleep(5)
            
        logger.info("Responders arrived or scene cleared. Returning to patrol.")
        self.on_clear()

    def on_enter_PATROL(self):
        logger.info("Entered PATROL State. Scanning for incidents...")
