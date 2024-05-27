# Robotic Arm Simulation with Hand Gesture Control

**Description**

This project simulates a robotic arm controlled by hand gestures using OpenCV and MediaPipe in Python, and rendered using Processing. The simulation shows a robotic arm in a 3D environment. The arm can move and detect if it's touching a cube in the scene. Movements and interactions are controlled by hand gestures detected through a webcam.

**Features**

* **3D Rendering:** Utilizes Processing with OpenGL for rendering 3D shapes.
* **Inverse Kinematics (IK):** Computes the position and orientation of the robotic arm.
* **Client-Server Communication:** Receives hand gesture data from a Python client via TCP/IP.
* **Gesture Detection:** Employs OpenCV and MediaPipe to detect hand gestures, such as "thumb up" and "thumb down".

**Installation**

**Prerequisites**

* Processing (https://processing.org/)
* Python 3 (https://www.python.org/downloads/)
* Python packages:
    * opencv-python
    * mediapipe
    * numpy

**Clone the Repository**

```bash
git clone [https://github.com/your-username/your-repository.git](https://github.com/your-username/your-repository.git)
cd your-repository
```

**Python Setup**
Install the necessary Python packages:
```bash
pip install opencv-python mediapipe numpy
```

**Usage**

***Run the Python Client:***
Open a terminal and navigate to the project directory and run the script:
```bash
python hand_detector.py
```
This script initializes the webcam and starts detecting hand gestures.

***Running the Processing Sketch:***
Open the Processing sketch and run it.

**Controls**

* Mouse Drag: Rotate the camera view in the Processing window.
* Hand Gestures: Use gestures like "thumb up" and "thumb down" in your right hand to control the z-position of the robotic arm.

**Ackowledgements**

* OpenCV
* MediaPipe
* Processing


