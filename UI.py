# UI using PyQt5, button for recording, not reviewed

import cv2
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QSizePolicy
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer, Qt

# Load the pre-trained Haar Cascade classifier for face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Start capturing video from the webcam (0 is the default camera)
cap = cv2.VideoCapture(0)

# Define the codec and create VideoWriter object (Optional: Recording)
fourcc = cv2.VideoWriter_fourcc(*'X264')
out = None  # VideoWriter will be initialized when recording starts

class FaceDetectionApp(QWidget):
    def __init__(self):
        super().__init__()
        self.is_recording = False  # Variable to track recording status
        self.initUI()

        # Timer for updating the video frame
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # Update frame every 30 ms

    def initUI(self):
        self.setWindowTitle('Face Detection with Recording')

        # Create layout
        layout = QVBoxLayout()

        # Create video label
        self.video_label = QLabel(self)
        self.video_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.video_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.video_label)

        # Create record button
        self.record_button = QPushButton('Start Recording', self)
        self.record_button.clicked.connect(self.toggle_recording)
        layout.addWidget(self.record_button)

        # Set layout
        self.setLayout(layout)
        self.setMinimumSize(640, 480)  # Set minimum size for the window

    def toggle_recording(self):
        global out
        # Toggle the recording flag
        self.is_recording = not self.is_recording
        
        # Update button text based on recording status
        if self.is_recording:
            self.record_button.setText('Stop Recording')
            print("Recording started")

            # Initialize the VideoWriter object when recording starts
            frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            out = cv2.VideoWriter('output.mkv', fourcc, 20.0, (frame_width, frame_height))
        else:
            self.record_button.setText('Start Recording')
            print("Recording stopped")

            # Release the VideoWriter object when recording stops
            if out:
                out.release()

    def update_frame(self):
        ret, frame = cap.read()

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        # Draw rectangles around faces
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

        # If recording, display a "Recording..." label on the frame and write the frame
        if self.is_recording:
            cv2.putText(frame, "Recording...", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3, cv2.LINE_AA)
            out.write(frame)

        # Resize frame to fit the QLabel (preserving aspect ratio)
        frame = self.resize_frame(frame)

        # Convert the frame to QImage for display in PyQt
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        q_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)

        # Display the image on the QLabel
        self.video_label.setPixmap(QPixmap.fromImage(q_image))

    def resize_frame(self, frame):
        # Get the QLabel dimensions
        label_width = self.video_label.width()
        label_height = self.video_label.height()

        # Get the frame dimensions
        frame_height, frame_width = frame.shape[:2]

        # Calculate the scaling factor to fit the frame within the QLabel
        scaling_factor = min(label_width / frame_width, label_height / frame_height)

        # Resize the frame while keeping the aspect ratio
        new_width = int(frame_width * scaling_factor)
        new_height = int(frame_height * scaling_factor)

        return cv2.resize(frame, (new_width, new_height))

    def closeEvent(self, event):
        # When the app is closed, release the video capture and writer
        cap.release()
        if out:
            out.release()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = FaceDetectionApp()
    main_window.show()
    sys.exit(app.exec_())
