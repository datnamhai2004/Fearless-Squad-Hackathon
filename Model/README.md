# Handwriting Recognition Model Using IMU Sensor Data

## Overview

This project involves a machine learning model trained to recognize handwritten digits based on data collected from IMU (Inertial Measurement Unit) sensors. Each dataset file contains sensor readings corresponding to a specific digit, with the file name indicating the digit label.

## Data Description

The data is located in the `data` folder and contains sensor readings collected during handwriting movements. Each file represents a sequence of IMU data points captured while writing a specific digit. The filename indicates the digit label, which serves as the ground truth for the model.

### Data Format

- Each file in the `data` folder follows the naming convention: `readings_<index>_digit_<label>.csv`.
  - Example: 
    - `readings_1_digit_0.csv` indicates the data is for the digit `0`.
    - `readings_1045_digit_9.csv` indicates the data is for the digit `9`.
- The data files are in CSV format, where each row represents a sensor reading consisting of multiple features such as accelerometer and gyroscope values.
- Each file typically includes readings over a fixed sequence length, such as 36 readings per sequence with 6 features each.

### Features

- **Accelerometer Data**: (accX, accY, accZ) — Measures acceleration in the X, Y, and Z axes.
- **Gyroscope Data**: (gyrX, gyrY, gyrZ) — Measures angular velocity in the X, Y, and Z axes.

## Model Description

The model is trained to recognize handwritten digits based on sequential IMU data. It uses deep learning techniques to classify digits by analyzing time-series data patterns.

### Training Process

- The model was trained using TensorFlow and Keras, leveraging a combination of sequential data modeling techniques tailored for time-series classification.
- Data preprocessing included normalization, reshaping, and data augmentation to improve model robustness.
- Training parameters were set to ensure the model generalizes well on unseen IMU data, using techniques such as dropout and batch normalization where applicable.

## Using the Model for Prediction

To use the model for predictions, you need to load the TensorFlow Lite model (`model_quantized.tflite`) and provide new IMU data formatted similarly to the training data.

### Steps to Predict Using the Model

1. **Load the Model**: Use TensorFlow Lite's `Interpreter` to load `model_quantized.tflite`.
2. **Prepare Input Data**: Format your input data as sequences of sensor readings matching the required shape `(36, 6)`.
3. **Run Inference**: Use the interpreter to set the input tensor, invoke the model, and retrieve the predicted digit.

### Example Code

```python
import numpy as np
import pandas as pd
import tensorflow as tf

# Load the TensorFlow Lite model
model_path = 'model_quantized.tflite'
interpreter = tf.lite.Interpreter(model_path=model_path)
interpreter.allocate_tensors()

# Load and preprocess input data
data = pd.read_csv('path/to/your/input.csv', header=None).to_numpy().astype(np.float32)
input_data = data.reshape(-1, 36, 6)  # Adjust based on your actual data structure

# Get input/output details
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Predict using the model
predictions = []
for sample in input_data:
    interpreter.set_tensor(input_details[0]['index'], [sample])
    interpreter.invoke()
    output_data = interpreter.get_tensor(output_details[0]['index'])
    predictions.append(output_data)

print("Predictions:", predictions)
