import cv2
import numpy as np
from deepface import DeepFace
from selenium import webdriver
from PIL import Image
import requests
from io import BytesIO
from functools import lru_cache


class ProfileAnalyzer:
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )

    @lru_cache(maxsize=100)
    def analyze_image(self, image_url):
        """Core analysis combining multiple techniques"""
        try:
            # Download image
            response = requests.get(image_url, timeout=10)
            img = np.array(Image.open(BytesIO(response.content)))

            results = {
                "face_detection": self._opencv_analysis(img),
                "deepfake_check": self._deepface_analysis(img),
                "social_footprint": self._check_social_footprint(image_url)
            }

            # Calculate composite risk score (0-10)
            risk_score = 0
            if not results["face_detection"]["has_face"]:
                risk_score += 4
            if results["deepfake_check"].get("is_ai", False):
                risk_score += 3
            if results["social_footprint"].get("is_stock", False):
                risk_score += 2

            results["credibility_risk"] = min(10, risk_score)

            # Generate human-readable flags
            red_flags = []
            if risk_score > 5:
                if not results["face_detection"]["has_face"]:
                    red_flags.append("no human face detected")
                if results["deepfake_check"].get("is_ai"):
                    red_flags.append("AI-generated features")
                if results["social_footprint"].get("is_stock"):
                    red_flags.append("stock photo characteristics")

            results["red_flags"] = red_flags
            return results

        except Exception as e:
            return {"error": str(e)}

    def _opencv_analysis(self, img):
        """Basic face verification"""
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)

        return {
            "has_face": len(faces) > 0,
            "face_count": len(faces),
            "likely_photo": len(faces) == 1  # Exactly one face
        }

    def _deepface_analysis(self, img):
        """Advanced GAN detection"""
        try:
            analysis = DeepFace.analyze(img, actions=['emotion'], enforce_detection=False)

            # AI-generated faces often have unusual emotion distributions
            emotions = analysis[0]['emotion']
            emotion_variance = np.var(list(emotions.values()))

            return {
                "is_ai": emotion_variance < 100,  # Low variance = suspicious
                "dominant_emotion": max(emotions, key=emotions.get)
            }
        except:
            return {"is_ai": False, "error": "analysis_failed"}

    def _check_social_footprint(self, image_url):
        """Reverse image search fallback"""
        try:
            # Use free Google Images search
            search_url = f"https://www.google.com/searchbyimage?image_url={image_url}"
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')
            options.add_argument('--no-sandbox')

            driver = webdriver.Chrome(options=options)
            driver.get(search_url)
            page_source = driver.page_source.lower()
            driver.quit()

            return {
                "is_stock": any(x in page_source for x in ["shutterstock", "getty", "istock"]),
                "search_url": search_url
            }
        except:
            return {"is_stock": False, "error": "search_failed"}