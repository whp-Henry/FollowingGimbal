from gpiozero import Servo
from time import sleep
import random
 
GPIOX=18
GPIOY=12
 
myCorrection=0.45
maxPW=(2.0+myCorrection)/1000
minPW=(1.05-myCorrection)/1000
 
servoX = Servo(GPIOX,min_pulse_width=minPW,max_pulse_width=maxPW)
servoY = Servo(GPIOY)

valueX = 0
valueY = 0

while True:
    valueX = valueX + random.random()/2-0.25
    valueY = valueY + random.random()/2-0.25

    while valueX >= 1 or valueX <= -1:
        valueX = 0
        print(f"!! X: {valueX}, Y: {valueY}")
    while valueY >= 1 or valueY <= -1:
        valueY = 0
        print(f"!! X: {valueX}, Y: {valueY}")
    servoX.value = valueX
    servoY.value = valueY
    print(f"~~ X: {valueX}, Y: {valueY}")
    sleep(0.1)
    servoX.detach()
    servoY.detach()
    sleep(0.1)
