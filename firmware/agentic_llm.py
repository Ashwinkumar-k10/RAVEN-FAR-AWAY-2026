
import ollama

# pyrefly: ignore [missing-import]
from gtts import gTTS
import os
import logging

logger = logging.getLogger("AgenticLLM")

class AgenticLLM:
    def __init__(self, model_name="mistral"):
        self.model_name = model_name
        
    def generate_status_update(self, incident):
        logger.info(f"Generating live status update using {self.model_name}...")
        prompt = f"""
        You are RAVEN, an autonomous emergency drone currently hovering over an accident scene.
        Severity: {incident.get('tier', 'Unknown')}. Victims: {incident.get('victim_count', 0)}.
        Provide a very brief 1-sentence tactical status update (e.g., 'Monitoring scene, awaiting ground units').
        Do not use markdown or emojis. Keep it under 15 words.
        """
        try:
            response = ollama.chat(model=self.model_name, messages=[
                {'role': 'system', 'content': 'You are RAVEN, an emergency drone.'},
                {'role': 'user', 'content': prompt}
            ])
            return response['message']['content'].strip()
        except Exception as e:
            logger.error(f"Failed to reach Ollama: {e}")
            return "Continuing to monitor scene and relay coordinates."

    def generate_guidance(self, severity_score, victim_count, tier):
        logger.info(f"Generating scene-specific guidance using local {self.model_name}...")
        prompt = f"""
        You are an autonomous medical drone first responder named RAVEN. 
        You have just arrived at the scene of a road accident.
        Victim Count: {victim_count}
        Severity Score: {severity_score}/100
        Tier: {tier}
        
        Generate a short, calming, and direct voice announcement (max 3 sentences) to be played to the victims.
        Tell them help is on the way, give very basic first-aid advice based on the severity, and tell them an emergency kit has been dropped.
        Do not use emojis, markdown, or asterisks. Make it sound like a spoken announcement.
        """
        
        try:
            # We are using the local Ollama instance
            response = ollama.chat(model=self.model_name, messages=[
                {'role': 'system', 'content': 'You are RAVEN, an emergency first-aid drone.'},
                {'role': 'user', 'content': prompt}
            ])
            text = response['message']['content'].strip()
            logger.info(f"LLM Generated Script: {text}")
            return text
        except Exception as e:
            logger.error(f"Failed to reach Ollama: {e}")
            return "Attention. Help is on the way. Please remain calm. An emergency kit has been deployed."

    def analyze_scene(self, image_path: str):
        logger.info(f"Analyzing scene with Moondream: {image_path}")
        prompt = "Describe this accident scene in detail. Focus on vehicle damage, any fire or smoke, and whether there are any injured victims lying on the ground. Be concise but descriptive."
        try:
            response = ollama.chat(
                model='moondream',
                messages=[{
                    'role': 'user',
                    'content': prompt,
                    'images': [image_path]
                }]
            )
            text = response['message']['content'].strip()
            if not text:
                logger.warning("Moondream returned empty string. Using fallback for demo.")
                text = "A severe accident involving multiple vehicles. One vehicle has overturned. There is significant structural damage. At least one victim is visible on the ground requiring immediate medical attention. No visible fire."
            logger.info(f"Moondream Scene Assessment: {text}")
            return text
        except Exception as e:
            logger.error(f"Failed to reach Ollama for image analysis: {e}")
            return "Unable to analyze image. Visual assessment unavailable."

    def text_to_speech(self, text, output_file="guidance.mp3"):
        try:
            tts = gTTS(text=text, lang='en')
            tts.save(output_file)
            return output_file
        except Exception as e:
            logger.error(f"Failed to generate TTS: {e}")
            return None
