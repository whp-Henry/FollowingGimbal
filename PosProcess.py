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


while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)
    # Convert the frame to grayscale (face detection is more accurate on grayscale images)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces in the grayscale frame
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

    # Get the center of the frame and the deadzone
    frame_center_x = frame.shape[1] // 2
    frame_center_y = frame.shape[0] // 2
    deadzone = frame.shape[0] // 8

    # Draw rectangles around the faces
    for (x, y, w, h) in faces:
        x_center = x + w // 2
        y_center = y + h // 2
        # cv2.circle(frame, (x_center, y_center), min(w, h) // 2, (0, 255, 0), 2)
        cv2.line(frame, (x_center + w // 3, y_center + h // 3), (x_center - w // 3, y_center - h // 3), (0, 0, 255), 2)
        cv2.line(frame, (x_center - w // 3, y_center + h // 3), (x_center + w // 3, y_center - h // 3), (0, 0, 255), 2)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(frame, f"Target",(x, y + h), font, 2,(255,255,255),2,cv2.LINE_AA)

    # Draw the center cross of the frame
    cv2.line(frame, (0, frame_center_y), (frame.shape[1], frame_center_y), (0, 255, 0), 2)
    cv2.line(frame, (frame_center_x, 0), (frame_center_x, frame.shape[0]), (0, 255, 0), 2)

    # Display the frame with detected faces
    if len(faces) > 0:
        # Get the coordinates of the first detected face
        (x, y, w, h) = faces[0]

        text_position = (50,100)
        text_position2 = (50,200)

        message1 = ""
        message2 = ""

        if x_center > frame_center_x + deadzone:
            message1 = "Too Right, turn left"
        elif x_center < frame_center_x - deadzone:
            message1 = "Too Left, turn right"
        if y_center > frame_center_y + deadzone:
            message2 = "Too Down, turn up"
        elif y_center < frame_center_y - deadzone:
            message2 = "Too Up, turn down"
        cv2.putText(frame, message1, text_position, font, 2, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(frame, message2, text_position2, font, 2, (255, 255, 255), 2, cv2.LINE_AA)

    # Draw a rectangle representing the deadzone
    cv2.rectangle(frame, 
                  (frame_center_x - deadzone, frame_center_y - deadzone), 
                  (frame_center_x + deadzone, frame_center_y + deadzone), 
                  (255, 255, 0), 2)

    
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
