# Description: Processing the position of the face, some drawings

# Import the necessary libraries
import cv2

# Load the pre-trained Haar Cascade classifier for face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Start capturing video from the webcam (0 is the default camera)
cap = cv2.VideoCapture(0)

# Define the codec and create VideoWriter object (Optional: Recording)
fourcc = cv2.VideoWriter_fourcc(*'X264')
ret, frame = cap.read()
out = cv2.VideoWriter('output.mkv', fourcc, 20.0, (frame.shape[1], frame.shape[0]))


def nothing(x):
    pass
# Create a black image, a window
cv2.namedWindow('Real-time Face Detection')
# create trackbars for color change
cv2.createTrackbar('A','Real-time Face Detection',40,100,nothing) # 1.01 - 2.0
cv2.createTrackbar('B','Real-time Face Detection',5,10,nothing) # 1 - 10




while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)
    # Convert the frame to grayscale (face detection is more accurate on grayscale images)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Detect faces in the grayscale frame
    scale_factor = cv2.getTrackbarPos('A', 'Real-time Face Detection') / 100 + 1.01
    faces = face_cascade.detectMultiScale(gray, scaleFactor=scale_factor, minNeighbors=cv2.getTrackbarPos('B', 'Real-time Face Detection'))
    
    # Draw rectangles around the faces
    for i, (x, y, w, h) in enumerate(faces):
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
        cv2.putText(frame, f"Target {i}",(x, y + h), cv2.FONT_HERSHEY_SIMPLEX, 2,(255,255,255),2,cv2.LINE_AA)

    cv2.putText(frame, f"Total: {len(faces)}",(50, 100), cv2.FONT_HERSHEY_SIMPLEX, 2,(255,255,255),2,cv2.LINE_AA)


    # Display the frame with detected faces
    cv2.imshow('Real-time Face Detection', frame)

    # Write the frame to the output video file
    out.write(frame)

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close windows
cap.release()
out.release()
cv2.destroyAllWindows()
