
from pathlib import Path
from PIL import Image
import streamlit as st

MODEL_PATH = Path(__file__).with_name("best.pt")

@st.cache_resource
def load_yolo_model():
    if not MODEL_PATH.exists():
        return None

    try:
        from ultralytics import YOLO
        return YOLO(str(MODEL_PATH))
    except Exception as e:
        st.error(f"Model gagal dimuatkan: {e}")
        return None


def analyze_image(pil_image, confidence=0.40):

    model = load_yolo_model()

    annotated = pil_image.copy()
    detections = []

    if model is None:
        return {
            "model_ready": False,
            "detections": [],
            "annotated": annotated,
            "long_status": "Belum dapat ditentukan",
            "color_status": "Belum dapat ditentukan",
            "notes": "Fail best.pt tidak ditemui atau gagal dimuatkan."
        }

    result = model.predict(
        source=pil_image.convert("RGB"),
        verbose=False
    )[0]

    probs = result.probs

    if probs is None:
        return {
            "model_ready": False,
            "detections": [],
            "annotated": annotated,
            "long_status": "Belum dapat ditentukan",
            "color_status": "Belum dapat ditentukan",
            "notes": "Model tidak menghasilkan skor klasifikasi."
        }

    names = result.names
    scores = probs.data.tolist()

    for class_id, score in enumerate(scores):
        detections.append({
            "name": str(names[class_id]),
            "confidence": float(score)
        })

    predicted_index = probs.top1
    predicted_name = str(names[predicted_index]).lower()

    if "panjang" in predicted_name or "long" in predicted_name:
        long_status = "Rambut panjang"
    elif "pendek" in predicted_name or "short" in predicted_name:
        long_status = "Rambut pendek"
    else:
        long_status = "Belum dapat ditentukan"

    if "berwarna" in predicted_name or "colored" in predicted_name:
        color_status = "Rambut berwarna"
    elif "semula_jadi" in predicted_name or "natural" in predicted_name:
        color_status = "Warna semula jadi"
    else:
        color_status = "Belum dapat ditentukan"

    return {
        "model_ready": True,
        "detections": detections,
        "annotated": annotated,
        "long_status": long_status,
        "color_status": color_status,
        "notes": (
            "Keputusan AI ialah saringan awal. "
            "Guru perlu menyemak dan mengesahkan keputusan."
        )
    }


def estimate_unusual_color(pil_image):
    return None
