from __future__ import annotations

from .base import TextRegionDetector


class PytesseractDetector(TextRegionDetector):
    def __init__(self, confidence_threshold=0.0): self.confidence_threshold = confidence_threshold

    def detect(self, image_path):
        try:
            import pytesseract
            from pytesseract import Output
        except ImportError as exc:
            raise RuntimeError("Optional OCR backend unavailable. Install pytesseract/tesseract only if the defense pilot is enabled.") from exc
        data = pytesseract.image_to_data(str(image_path), output_type=Output.DICT)
        boxes = []
        for i, text in enumerate(data.get("text", [])):
            try: conf = float(data["conf"][i]) / 100
            except Exception: conf = 0
            if text.strip() and conf >= self.confidence_threshold:
                x, y, w, h = (int(data[k][i]) for k in ("left", "top", "width", "height"))
                boxes.append([x, y, x + w, y + h])
        return boxes

