# network-robot
a robot controlled via local network
Pinout used:
Bumper left 17
Bumper right 4
Level shifter to make LED strip work at 12V:
LED Green 3
LED red	2
L298N motor controller:
Motor 1 22 & 24
Motor 2 23 & 25

scripot that holds the code: app.py


Start with :

uvicorn app:app --host 0.0.0.0 --port 8000

Speed of Video streams can  be improved by reducing the resolution.
Assumes RPI 5 and two wide angle camera modules connected via CSI.
As seen on element14 presents.

Start the app. Navigate to the Ip adress of the host port 8000
-> use the arrow keys on the keyboard to controll the robot.
LED not implemented as the contact was unreliable and hard to film.

