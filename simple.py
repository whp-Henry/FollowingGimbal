# Description: A simple real-time face detection program using OpenCV

# Import the necessary libraries
import cv2

# Load the pre-trained Haar Cascade classifier for face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Start capturing video from the webcam (0 is the default camera)
cap = cv2.VideoCapture(0)

# Define the codec and create VideoWriter object (Optional: Recording)
fourcc = cv2.VideoWriter_fourcc(*'X264') # MJPG (.mp4), DIVX (.avi), X264 (.mkv)
out = cv2.VideoWriter('output.mkv', fourcc, 20.0, (1920, 1080))

# For any resolution of the Camera: 
ret, frame = cap.read()
out = cv2.VideoWriter('output.mkv', fourcc, 20.0, (frame.shape[1], frame.shape[0]))


while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
    # frame = cv2.flip(frame, 1)

    # Save a copy(optional)
    # original_frame = frame.copy()

    # Convert the frame to grayscale (face detection is more accurate on grayscale images)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Detect faces in the grayscale frame
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)
    
    # Draw rectangles around the faces
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
    
    # Display the frame with detected faces
    cv2.imshow('Real-time Face Detection', frame)

    # Write the frame to the output video file
    out.write(frame)
    # If you want to save the original frame:
    # out.write(original_frame)

    # Break the loop if 'q' is pressed (Optional: esc: 27)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close windows
cap.release()
out.release()
cv2.destroyAllWindows()
