import os
import cv2

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "assets", "models")
YUNET_PATH = os.path.join(MODEL_DIR, "face_detection_yunet_2023mar.onnx")
SFACE_PATH = os.path.join(MODEL_DIR, "face_recognition_sface_2021dec.onnx")

THRESHOLD = 0.363   # OpenCV's recommended cosine-similarity threshold for SFace


class FaceEngine:
    def __init__(self):
        self.detector = cv2.FaceDetectorYN.create(
            YUNET_PATH, "", (320, 320), 0.8, 0.3, 5000)
        self.recognizer = cv2.FaceRecognizerSF.create(SFACE_PATH, "")

    def detect(self, frame):
        h, w = frame.shape[:2]
        self.detector.setInputSize((w, h))
        _, faces = self.detector.detect(frame)
        return [] if faces is None else list(faces)

    def embed(self, frame, face):
        aligned = self.recognizer.alignCrop(frame, face)
        return self.recognizer.feature(aligned)

    def score(self, feature_a, feature_b):
        return self.recognizer.match(
            feature_a, feature_b, cv2.FaceRecognizerSF_FR_COSINE)

    def identify(self, feature, known):
        """known = {id: [features]}. Returns (id or None, best_score)."""
        best_id, best_score = None, -1.0
        for emp_id, saved_list in known.items():
            for saved in saved_list:
                s = self.score(feature, saved)
                if s > best_score:
                    best_id, best_score = emp_id, s
        if best_score >= THRESHOLD:
            return best_id, best_score
        return None, best_score