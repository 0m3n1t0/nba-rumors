# Models

`face_detection_yunet_2023mar.onnx` - YuNet face detector from the OpenCV Model Zoo
(https://github.com/opencv/opencv_zoo/tree/main/models/face_detection_yunet), Apache License 2.0.
SHA-256: 8f2383e4dd3cfbb4553ea8718107fc0423210dc964f9f4280604804ed2552fa4

Used by `src/render.py` (`face_focus`) to place crops, captions and motion around faces.
If the file is missing, the renderer falls back to OpenCV's built-in Haar detector.
