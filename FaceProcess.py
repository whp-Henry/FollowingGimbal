# Detect faces and Crop them out to seperate windows

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
    # Convert the frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Detect faces in the grayscale frame
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)
    
    # Loop through each detected face
    for i, (x, y, w, h) in enumerate(faces):
        x_center = x + w // 2
        y_center = y + h // 2
        # cv2.circle(frame, (x_center, y_center), min(w, h) // 2, (0, 255, 0), 2)
        cv2.line(frame, (x_center + w // 3, y_center + h // 3), (x_center - w // 3, y_center - h // 3), (0, 0, 255), 2)
        cv2.line(frame, (x_center - w // 3, y_center + h // 3), (x_center + w // 3, y_center - h // 3), (0, 0, 255), 2)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(frame, f"Target",(x, y + h), font, 2,(255,255,255),2,cv2.LINE_AA)
        
        # Crop out each face
        # Add some padding around the face
        padding = 20
        x_pad = max(0, x - padding)
        y_pad = max(0, y - padding)
        w_pad = min(frame.shape[1] - x_pad, w + 2 * padding)
        h_pad = min(frame.shape[0] - y_pad, h + 2 * padding)
        
        # Crop the face from the original frame
        cropped_face = frame[y_pad:y_pad+h_pad, x_pad:x_pad+w_pad]
        
        # Resize the cropped face for uniform display (optional)
        cropped_face_resized = cv2.resize(cropped_face, (200, 200))
        
        # Display the cropped face in a separate window for each face
        cv2.imshow(f'Cropped Face {i+1}', cropped_face_resized)
    


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
