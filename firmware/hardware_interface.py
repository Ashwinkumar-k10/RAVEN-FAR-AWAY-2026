import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("HardwareInterface")

class HardwareInterface:
    def __init__(self, mock_mode=True):
        self.mock_mode = mock_mode
        if self.mock_mode:
            logger.info("Hardware Interface initialized in MOCK mode.")
        else:
            logger.info("Hardware Interface initialized in LIVE mode.")
            # Initialization code for actual hardware (GPIO, Serial, Pygame) goes here

    def get_gps_location(self):
        # Mocking GPS coords somewhere on a highway
        if self.mock_mode:
            return {"latitude": 28.535517, "longitude": 77.391029}
        else:
            # Read from Neo-6M module
            pass

    def release_payload(self):
        if self.mock_mode:
            logger.info("[SERVO MOCK] Triggering MG996R servo to release payload!")
            time.sleep(1)
            logger.info("[SERVO MOCK] Payload released successfully.")
        else:
            # Send PWM signal to GPIO
            pass

    def play_audio(self, audio_file_path="guidance.mp3"):
        if self.mock_mode:
            logger.info(f"[AUDIO MOCK] Playing audio file: {audio_file_path}")
            time.sleep(2)
        else:
            try:
                import pygame
                pygame.mixer.init()
                pygame.mixer.music.load(audio_file_path)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    time.sleep(1)
            except Exception as e:
                logger.error(f"Failed to play audio: {e}")

    def send_sms(self, phone_number, message):
        if self.mock_mode:
            logger.info(f"[SMS MOCK] Sending SMS to {phone_number}: '{message}'")
        else:
            # Integration with Africa's Talking API
            pass
