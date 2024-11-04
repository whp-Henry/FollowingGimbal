import cv2
from picamera2 import Picamera2
# from gpiozero import Servo
from time import sleep, time
import board
from adafruit_motor import servo
from adafruit_pca9685 import PCA9685

# Load the pre-trained Haar Cascade classifier for face detection
face_cascade = cv2.CascadeClassifier('/home/admin/Desktop/FollowingGimbal/RasPi/haarcascade_frontalface_default.xml')

picam2 = Picamera2()
picam2.preview_configuration.main.size = (640, 480)
# picam2.preview_configuration.main.size = (1280, 960)
picam2.preview_configuration.main.format = "RGB888"
picam2.preview_configuration.align()
picam2.configure("preview")
picam2.start()


# Get the dimensions for deadzone calculations
frame_center_x = picam2.preview_configuration.main.size[0] // 2
frame_center_y = picam2.preview_configuration.main.size[1] // 2
deadzone = frame_center_y // 4  # Use a portion of the height for deadzone

idle_start = 0
idleing = False

servoSensitivity = 1.5
font = cv2.FONT_HERSHEY_SIMPLEX

i2c = board.I2C()
pca = PCA9685(i2c)
pca.frequency = 50

servoX = servo.Servo(pca.channels[0], min_pulse=500, max_pulse=2400)
servoY = servo.Servo(pca.channels[1], min_pulse=1000, max_pulse=2000)
servoX.angle = 90
servoY.angle = 90
# Current Servo angles
valueX = 90
valueY = 90

try:
    while True:
        start_time = time()

        im = picam2.capture_array()
        # Flip the image horizontally for a mirror effect
        im = cv2.flip(im, 1)

        # Convert the image to grayscale for face detection
        gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)

        # Perform face detection
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.25, minNeighbors=5, minSize=(100, 100))

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
            changeX = 0
            changeY = 0
            if x_center > frame_center_x + deadzone:
                message1 = ">"
                changeX = servoSensitivity
            elif x_center < frame_center_x - deadzone:
                message1 = "<"
                changeX = - servoSensitivity
            if y_center > frame_center_y + deadzone:
                message2 = "v"
                changeY = servoSensitivity
            elif y_center < frame_center_y - deadzone:
                message2 = "^"
                changeY = - servoSensitivity
            
            if valueX + changeX > 0 and valueX + changeX < 180 and changeX != 0:
                valueX = valueX + changeX
                servoX.angle = valueX
            if valueY + changeY > 0 and valueY + changeY < 180 and changeY != 0:
                valueY = valueY + changeY
                servoY.angle = valueY
            print(f"X: {round(valueX,2)}, Y: {round(valueY,2)}")


            # Display position messages
            cv2.putText(im, message1, (frame_center_x, frame_center_y), font, 10, (255, 255, 255), 2, cv2.LINE_AA)
            # cv2.putText(im, message1, (52, 102), font, 1, (0,0,0), 2, cv2.LINE_AA)

            cv2.putText(im, message2, (frame_center_x, frame_center_y+200), font, 10, (255, 255, 255), 2, cv2.LINE_AA)
            # cv2.putText(im, message2, (52, 202), font, 1, (0,0,0), 2, cv2.LINE_AA)
            idleing = False
            idle_period = 0

            
        else:
            if idleing == False:
                idleing =  True
                idle_start = time()
            idle_period = time() - idle_start
            if idle_period > 5 and idle_period < 5.1 and idleing == True:
                valueX = 90
                valueY = 90
                servoX.angle = 90
                servoY.angle = 90
                print("No face detected")
                cv2.putText(im, "Center", (frame_center_x-130, frame_center_y+20), font, 3, (255, 255, 255), 5, cv2.LINE_AA)


        # Calculate and display FPS
        end_time = time()
        fps = 1 / (end_time - start_time)
        cv2.putText(im, f"FPS: {fps:.2f}", (10, 30), font, 1, (255, 255, 255), 2, cv2.LINE_AA)

        cv2.putText(im, f"Idle: {round(idle_period,2)}", (10, 80), font, 1, (255, 255, 255), 2, cv2.LINE_AA)


        # Display the image with detected faces
        cv2.imshow("Face Detection", im)

        # Break the loop when 'q' is pressed
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('w'):
            servoX.angle = 90
            servoY.angle = 90
            valueX = 90
            valueY = 90


finally:
    # Release resources
    cv2.destroyAllWindows()
    picam2.stop()
    picam2.close()
    servoX.angle = None
    servoY.angle = None
    pca.deinit()
