import cv2
from picamera2 import Picamera2
from gpiozero import Servo
from time import sleep, time
import random
import board
from adafruit_motor import servo
from adafruit_pca9685 import PCA9685


# Choose your tracking algorithm: CSRT, KCF, MIL, etc.
tracker_type = 'MEDIANFLOW'  # Options: 'BOOSTING', 'MIL', 'KCF', 'TLD', 'MEDIANFLOW', 'MOSSE', 'CSRT'

# Create a tracker based on the selected algorithm
if tracker_type == 'BOOSTING':
    tracker = cv2.legacy.TrackerBoosting_create()
if tracker_type == 'MIL':
    tracker = cv2.legacy.TrackerMIL_create()
if tracker_type == 'KCF':
    tracker = cv2.legacy.TrackerKCF_create()
if tracker_type == 'TLD':
    tracker = cv2.legacy.TrackerTLD_create()
if tracker_type == 'MEDIANFLOW':
    tracker = cv2.legacy.TrackerMedianFlow_create()
if tracker_type == 'MOSSE':
    tracker = cv2.legacy.TrackerMOSSE_create()
if tracker_type == "CSRT":
    tracker = cv2.TrackerCSRT_create()
# else:
#     raise ValueError(f"Unknown tracker type: {tracker_type}")

# Initialize face detection
face_cascade = cv2.CascadeClassifier('/home/admin/Desktop/FollowingGimbal/RasPi/haarcascade_frontalface_default.xml')

# Initialize the Picamera2
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

GPIOX=18
GPIOY=12
 
maxPW=2400
minPW=500
 
valueX = 90
valueY = 90
idle_start = 0
idleing = False
idle_period = 0

servoSensitivity = 1.5
font = cv2.FONT_HERSHEY_SIMPLEX


i2c = board.I2C()
pca = PCA9685(i2c)
pca.frequency = 50

servoX = servo.Servo(pca.channels[0], min_pulse=500, max_pulse=2400)
servoY = servo.Servo(pca.channels[4], min_pulse=1000, max_pulse=2000)
servoX.angle = 90
servoY.angle = 90


# Flag to start tracking after face detection
tracking = False
bbox = None
x, y, w, h = 0, 0, 0, 0

try:
    while True:
        start_time = time()

        # Capture frame-by-frame
        im = picam2.capture_array()
        im = cv2.flip(im, 1)

        cv2.line(im, (0, frame_center_y), (im.shape[1], frame_center_y), (0, 255, 0), 2)
        cv2.line(im, (frame_center_x, 0), (frame_center_x, im.shape[0]), (0, 255, 0), 2)
        # Draw a rectangle representing the deadzone
        cv2.rectangle(im, 
            (frame_center_x - deadzone, frame_center_y - deadzone), 
            (frame_center_x + deadzone, frame_center_y + deadzone), 
            (255, 255, 0), 2)


        if not tracking:
            cv2.putText(im, "DETECTING", (frame_center_x-130, frame_center_y+20), font, 3, (255, 255, 255), 5, cv2.LINE_AA)

            # Face detection
            print("Face Detection")
            gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)

            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.15, minNeighbors=5, minSize=(100, 100))

            if len(faces) > 0:
                # Initialize tracker with the first detected face
                bbox = tuple(faces[0])  # (x, y, w, h)
                tracker.init(im, bbox)
                tracking = True
                print("Tracking started...")
                cv2.putText(im, "START", (frame_center_x-500, frame_center_y+200), font, 3, (0, 0, 255), 5, cv2.LINE_AA)
                (x, y, w, h) = faces[0]
                cv2.rectangle(im, (x, y), (x + w, y + h), (255, 255, 0), 15)
                idleing = False
            else:
                cv2.putText(im, "FAIL", (frame_center_x-500, frame_center_y+200), font, 3, (0, 0, 255), 5, cv2.LINE_AA)
                print("Detection Failed")
                bbox = None
                

        else:
            # Update tracker
            x, y, w, h = [int(v) for v in bbox]
            cv2.rectangle(im, (x, y), (x + w, y + h), (255, 255, 255), 20)
            success, bbox = tracker.update(im)
            x_center = x + w // 2
            y_center = y + h // 2
            cv2.line(im, (x_center + w // 3, y_center + h // 3), (x_center - w // 3, y_center - h // 3), (255, 255, 255), 20)
            cv2.line(im, (x_center - w // 3, y_center + h // 3), (x_center + w // 3, y_center - h // 3), (255, 255, 255), 20)
            if success:
                # Tracking successful, draw bounding box
                x, y, w, h = [int(v) for v in bbox]
                cv2.rectangle(im, (x, y), (x + w, y + h), (0, 255, 0), 10)
                idleing = False
            else:
                # Tracking failure, switch back to detection mode
                tracking = False
                idleing = True
                print("Tracking failed. Reverting to face detection.")
                bbox = None
            if random.randint(0,6)==5:
                tracking = False
                print("Refresh Tracking")

        if bbox is not None:
            x, y, w, h = [int(v) for v in bbox]
            x_center = x + w // 2
            y_center = y + h // 2

            # Draw rectangle around the face
            # cv2.rectangle(im, (x, y), (x + w, y + h), (255, 0, 0), 2)
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
            # print(f"X: {round(valueX,2)}, Y: {round(valueY,2)}")


            # Display position messages
            cv2.putText(im, message1, (frame_center_x, frame_center_y), font, 10, (255, 255, 255), 2, cv2.LINE_AA)

            cv2.putText(im, message2, (frame_center_x, frame_center_y+200), font, 10, (255, 255, 255), 2, cv2.LINE_AA)
            idleing = False
            idle_period = 0


        if idleing:
            if idle_start == None:
                idle_start = time()
            idle_period = time() - idle_start
            if idle_period > 5 and idle_period < 5.1 and idleing == True:
                valueX = 90
                valueY = 90
                servoX.angle = 90
                servoY.angle = 90
                print("No face detected")
                cv2.putText(im, "Center", (frame_center_x-130, frame_center_y+20), font, 3, (255, 255, 255), 5, cv2.LINE_AA)
        else:
            idle_start = None


        end_time = time()
        fps = 1 / (end_time - start_time)
        cv2.putText(im, f"FPS: {fps:.2f}", (10, 30), font, 1, (255, 255, 255), 2, cv2.LINE_AA)

        cv2.putText(im, f"Idle: {round(idle_period,2)}", (10, 80), font, 1, (255, 255, 255), 2, cv2.LINE_AA)





        # Display the result
        cv2.imshow("Object Tracking", im)

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
    pca.deinit()
    servoX.angle = None
    servoY.angle = None
