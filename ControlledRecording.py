# Description: Record video clips as commanded and save as seperated files

# Import the necessary libraries
import cv2
import time

# Load the pre-trained Haar Cascade classifier for face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Start capturing video from the webcam (0 is the default camera)
cap = cv2.VideoCapture(0)

# Define the codec
fourcc = cv2.VideoWriter_fourcc(*'X264')
out = None  # Initialize the video writer as None
is_recording = False  # Flag to control recording state
recording_counter = 0  # Counter for multiple clips


while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)
    # Convert the frame to grayscale (face detection is more accurate on grayscale images)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Detect faces in the grayscale frame
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)
    
    # Draw rectangles around the faces
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(frame, f"Target", (x, y + h), font, 2, (255, 255, 255), 2, cv2.LINE_AA)

    # Display recording status on the frame and write frame to output video
    if is_recording:
        cv2.putText(frame, "Recording...", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3, cv2.LINE_AA)
        if out is None:  # Initialize VideoWriter when recording starts
            timestamp = time.strftime("%y%m%d-%H%M%S") # 241016-220234_clip1
            filename = f'{timestamp}_clip{recording_counter}.mkv'  # New file for each clip
            out = cv2.VideoWriter(filename, fourcc, 20.0, (frame.shape[1], frame.shape[0]))
        out.write(frame)  # Write the frame to the video file

    # Display the frame with detected faces and recording status
    cv2.imshow('Real-time Face Detection', frame)

    # Check for key presses
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):  # Quit the loop if 'q' is pressed
        break
    elif key == ord('r'):  # Toggle recording on 'r' press
        is_recording = not is_recording
        if is_recording: # Start new recording
            recording_counter += 1  # Increment the clip counter when recording starts
        else: # Stop old recording
            if out is not None:  # Stop recording and release the writer
                out.release()
                out = None
        print(f"Recording: {'On' if is_recording else 'Off'}")

# Release the webcam and close windows
cap.release()
if out is not None:
    out.release()
cv2.destroyAllWindows()
