import cv2
from picamera2 import Picamera2
from time import time

# Choose your tracking algorithm: CSRT, KCF, MIL, etc.
tracker_type = 'MOSSE'  # Options: 'BOOSTING', 'MIL', 'KCF', 'TLD', 'MEDIANFLOW', 'MOSSE', 'CSRT'

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
picam2.preview_configuration.main.size = (800, 600)
picam2.preview_configuration.main.format = "RGB888"
picam2.preview_configuration.align()
picam2.configure("preview")
picam2.start()

# Flag to start tracking after face detection
tracking = False
bbox = None

try:
    while True:
        start_time = time()

        # Capture frame-by-frame
        im = picam2.capture_array()

        if not tracking:
            # Face detection
            gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.15, minNeighbors=5, minSize=(30, 30))

            if len(faces) > 0:
                # Initialize tracker with the first detected face
                bbox = tuple(faces[0])  # (x, y, w, h)
                tracker.init(im, bbox)
                tracking = True
                print("Tracking started...")

        else:
            # Update tracker
            success, bbox = tracker.update(im)
            if success:
                # Tracking successful, draw bounding box
                x, y, w, h = [int(v) for v in bbox]
                cv2.rectangle(im, (x, y), (x + w, y + h), (0, 255, 0), 2)
            else:
                # Tracking failure, switch back to detection mode
                tracking = False
                print("Tracking failed. Reverting to face detection.")

        # Display the result
        cv2.imshow("Object Tracking", im)

        # Break the loop when 'q' is pressed
        if cv2.waitKey(1) == ord('q'):
            break

finally:
    # Release resources
    cv2.destroyAllWindows()
    picam2.stop()
    picam2.close()
