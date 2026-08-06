from __future__ import annotations

from abc import ABC, abstractmethod


class TextRegionDetector(ABC):
    @abstractmethod
    def detect(self, image_path):
        """Return pixel bounding boxes [x1, y1, x2, y2]."""


class OCRMaskDefense:
    def __init__(self, detector: TextRegionDetector, fill=(127, 127, 127)):
        self.detector, self.fill = detector, tuple(fill)

    def mask(self, image_path, output_path):
        from PIL import Image, ImageDraw
        image = Image.open(image_path).convert("RGB")
        boxes = self.detector.detect(image_path)
        draw = ImageDraw.Draw(image)
        for box in boxes: draw.rectangle(tuple(box), fill=self.fill)
        image.save(output_path)
        return {"detected_boxes": boxes, "output_path": str(output_path)}

