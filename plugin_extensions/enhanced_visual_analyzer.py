#!/usr/bin/env python3
"""
EnhancedVisualAnalyzer plugin for the crawler.

Uses OpenCV's DNN module for object detection on the first image found in the HTML content.
Configuration parameters (nested):
  - model:
      prototxt: string (default: "MobileNetSSD_deploy.prototxt.txt")
      caffemodel: string (default: "MobileNetSSD_deploy.caffemodel")
  - detection:
      confidence_threshold: float (default: 0.2)
Requires: opencv-python, numpy, requests, beautifulsoup4

Note: Ensure the model files are available in the working directory or provide absolute paths in the configuration.
"""
from plugins import PluginBase
from bs4 import BeautifulSoup
import cv2
import numpy as np
import urllib.parse
import requests

class EnhancedVisualAnalyzer(PluginBase):
    def __init__(self):
        # Default configuration parameters
        self.prototxt = "MobileNetSSD_deploy.prototxt.txt"
        self.caffemodel = "MobileNetSSD_deploy.caffemodel"
        self.confidence_threshold = 0.2
        self.labels = [
            "background", "aeroplane", "bicycle", "bird", "boat",
            "bottle", "bus", "car", "cat", "chair", "cow",
            "diningtable", "dog", "horse", "motorbike", "person",
            "pottedplant", "sheep", "sofa", "train", "tvmonitor"
        ]
        self.net = cv2.dnn.readNetFromCaffe(self.prototxt, self.caffemodel)

    def configure(self, settings):
        # Update nested configuration options if provided
        model_config = settings.get("model", {})
        self.prototxt = model_config.get("prototxt", self.prototxt)
        self.caffemodel = model_config.get("caffemodel", self.caffemodel)
        detection_config = settings.get("detection", {})
        self.confidence_threshold = detection_config.get("confidence_threshold", self.confidence_threshold)
        # Reload the network with new model files if provided
        self.net = cv2.dnn.readNetFromCaffe(self.prototxt, self.caffemodel)

    def process(self, html, url):
        soup = BeautifulSoup(html, "html.parser")
        img_tag = soup.find("img")
        if not img_tag or not img_tag.get("src"):
            return "No image found."
        img_url = urllib.parse.urljoin(url, img_tag["src"])
        try:
            response = requests.get(img_url, stream=True)
            response.raise_for_status()
            data = np.asarray(bytearray(response.content), dtype="uint8")
            image = cv2.imdecode(data, cv2.IMREAD_COLOR)
            if image is None:
                return "Failed to decode image."
        except Exception as e:
            return f"Error processing image: {e}"
        
        # Prepare image for object detection
        (h, w) = image.shape[:2]
        blob = cv2.dnn.blobFromImage(cv2.resize(image, (300, 300)), 0.007843, (300, 300), 127.5)
        self.net.setInput(blob)
        detections = self.net.forward()
        
        results = []
        # Loop over the detections and filter based on confidence threshold
        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > self.confidence_threshold:
                idx = int(detections[0, 0, i, 1])
                label = self.labels[idx] if idx < len(self.labels) else "Unknown"
                results.append({"label": label, "confidence": float(confidence)})
        return results if results else "No objects detected with sufficient confidence."
