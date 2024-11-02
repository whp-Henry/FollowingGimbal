from gpiozero import Servo
from time import sleep
 
GPIOX=18
GPIOY=12
 
myCorrection=0.45
maxPW=(2.0+myCorrection)/1000
minPW=(1.0-myCorrection)/1000
 
servoX = Servo(GPIOX,min_pulse_width=minPW,max_pulse_width=maxPW)
servoY = Servo(GPIOY)


while True:
    servoX.min()
    servoY.min()
    sleep(0.05)
    servoX.detach()
    servoY.detach()
    sleep(2)
    servoX.mid()
    servoY.mid()
    sleep(0.05)
    servoX.detach()
    servoY.detach()
    sleep(2)
    servoX.max()
    servoY.max()
    sleep(0.05)
    servoX.detach()
    servoY.detach()
    sleep(2)
    servoX.mid()
    servoY.mid()
    sleep(0.05)
    servoX.detach()
    servoY.detach()
    sleep(2)
