import cv2
from picamera2 import Picamera2

# Load the pre-trained Haar Cascade classifier for face detection
face_cascade = cv2.CascadeClassifier('/home/admin/Desktop/FollowingGimbal/RasPi/haarcascade_frontalface_default.xml')

picam2 = Picamera2()
picam2.preview_configuration.main.size = (1280, 960)
picam2.preview_configuration.main.format = "RGB888"
picam2.preview_configuration.align()
picam2.configure("preview")
picam2.start()

# Get the dimensions for deadzone calculations
frame_center_x = picam2.preview_configuration.main.size[0] // 2
frame_center_y = picam2.preview_configuration.main.size[1] // 2
deadzone = frame_center_y // 4  # Use a portion of the height for deadzone

try:
    while True:
        im = picam2.capture_array()
        # Flip the image horizontally for a mirror effect
        im = cv2.flip(im, 1)

        # Convert the image to grayscale for face detection
        gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)

        # Perform face detection
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

        # Draw the center cross of the frame
        cv2.line(im, (0, frame_center_y), (im.shape[1], frame_center_y), (0, 255, 0), 2)
        cv2.line(im, (frame_center_x, 0), (frame_center_x, im.shape[0]), (0, 255, 0), 2)
        # Draw a rectangle representing the deadzone
        cv2.rectangle(im, 
                          (frame_center_x - deadzone, frame_center_y - deadzone), 
                          (frame_center_x + deadzone, frame_center_y + deadzone), 
                          (255, 255, 0), 2)

        # Draw rectangles around the detected faces and provide positional feedback
        if len(faces) > 0:
            (x, y, w, h) = faces[0]
            x_center = x + w // 2
            y_center = y + h // 2

            # Draw rectangle around the face
            cv2.rectangle(im, (x, y), (x + w, y + h), (255, 0, 0), 2)
            cv2.line(im, (x_center + w // 3, y_center + h // 3), (x_center - w // 3, y_center - h // 3), (0, 0, 255), 2)
            cv2.line(im, (x_center - w // 3, y_center + h // 3), (x_center + w // 3, y_center - h // 3), (0, 0, 255), 2)

            # Position messages
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

            # Display position messages
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(im, message1, (50, 100), font, 1, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.putText(im, message1, (52, 102), font, 1, (0,0,0), 2, cv2.LINE_AA)

            cv2.putText(im, message2, (50, 200), font, 1, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.putText(im, message2, (52, 202), font, 1, (0,0,0), 2, cv2.LINE_AA)


            

        # Display the image with detected faces
        cv2.imshow("Face Detection", im)

        # Break the loop when 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    # Release resources
    cv2.destroyAllWindows()
    picam2.stop()
    picam2.close()
