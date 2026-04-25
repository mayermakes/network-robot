from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse, StreamingResponse
from gpiozero import LED
from picamera2 import Picamera2
import cv2

app = FastAPI()

# ---- MOTOR PINS ----
# Left motor
L1 = LED(22)
L2 = LED(24)

# Right motor
R1 = LED(23)
R2 = LED(25)


def stop():
    L1.off(); L2.off()
    R1.off(); R2.off()


def forward():
    L1.on();  L2.off()
    R1.on();  R2.off()


def reverse():
    L1.off(); L2.on()
    R1.off(); R2.on()


def left():
    # left motor stop, right forward
    L1.off(); L2.on()
    R1.on();  R2.off()


def right():
    # left forward, right stop
    L1.on();  L2.off()
    R1.off(); R2.on()


# ---- CAMERAS ----
cam0 = Picamera2(1)
cam1 = Picamera2(0)

config0 = cam0.create_video_configuration(main={"size": (640, 480)})
config1 = cam1.create_video_configuration(main={"size": (640, 480)})

cam0.configure(config0)
cam1.configure(config1)

cam0.start()
cam1.start()


def generate(camera):
    while True:
        frame = camera.capture_array()
        frame = cv2.rotate(frame, cv2.ROTATE_180)

        _, jpeg = cv2.imencode(".jpg", frame)

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" +
            jpeg.tobytes() +
            b"\r\n"
        )


# ---- HTML UI ----
html = """
<!DOCTYPE html>
<html>
<head>
    <title>Robot Control</title>
    <style>
        body { text-align: center; font-family: sans-serif; }
        .cams {
            display: flex;
            justify-content: center;
        }
        img {
            width: 45%;
            margin: 5px;
        }
    </style>
</head>
<body>
    <h1>Robot Control + Dual Camera</h1>

    <div class="cams">
        <img src="/cam0">
        <img src="/cam1">
    </div>

    <p>
        ⬆️ Forward |
        ⬇️ Reverse |
        ⬅️ Left |
        ➡️ Right |
        Release = Stop
    </p>

    <p id="status">Idle</p>

    <script>
        const ws = new WebSocket("ws://" + location.host + "/ws");

        document.addEventListener("keydown", (e) => {
            if (e.repeat) return;

            if (e.key === "ArrowUp") ws.send("forward");
            else if (e.key === "ArrowDown") ws.send("reverse");
            else if (e.key === "ArrowLeft") ws.send("left");
            else if (e.key === "ArrowRight") ws.send("right");
        });

        document.addEventListener("keyup", (e) => {
            if (["ArrowUp","ArrowDown","ArrowLeft","ArrowRight"].includes(e.key)) {
                ws.send("stop");
            }
        });

        ws.onmessage = (event) => {
            document.getElementById("status").innerText = event.data;
        };
    </script>
</body>
</html>
"""


# ---- ROUTES ----
@app.get("/")
def index():
    return HTMLResponse(html)


@app.get("/cam0")
def cam0_feed():
    return StreamingResponse(generate(cam0),
        media_type="multipart/x-mixed-replace; boundary=frame")


@app.get("/cam1")
def cam1_feed():
    return StreamingResponse(generate(cam1),
        media_type="multipart/x-mixed-replace; boundary=frame")


# ---- WEBSOCKET CONTROL ----
@app.websocket("/ws")
async def ws_endpoint(websocket: WebSocket):
    await websocket.accept()

    while True:
        cmd = await websocket.receive_text()

        if cmd == "forward":
            forward()
            await websocket.send_text("FORWARD")

        elif cmd == "reverse":
            reverse()
            await websocket.send_text("REVERSE")

        elif cmd == "left":
            left()
            await websocket.send_text("LEFT")

        elif cmd == "right":
            right()
            await websocket.send_text("RIGHT")

        elif cmd == "stop":
            stop()
            await websocket.send_text("STOP")
