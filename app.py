from flask import Flask, render_template, Response, jsonify
import cv2
from deepface import DeepFace
from collections import Counter

app = Flask(__name__)

cap = None
running = False
emotion_counter = Counter()

# Load Haar Cascade for face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def map_emotion(emotion):
    if emotion in ['happy', 'surprise']:
        return "Engaged"
    elif emotion in ['neutral', 'sad']:
        return "Bored/Neutral"
    elif emotion in ['angry', 'fear', 'disgust']:
        return "Confused/Frustrated"
    return "No Face Detected"

def generate_frames():
    global cap, running, emotion_counter
    while running and cap:
        success, frame = cap.read()
        if not success:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        if len(faces) == 0:
            state = "No Face Detected"
        else:
            # Take the first face only
            (x, y, w, h) = faces[0]
            face_img = frame[y:y+h, x:x+w]

            try:
                result = DeepFace.analyze(face_img, actions=['emotion'], enforce_detection=False)
                dominant_emotion = result[0]['dominant_emotion']
                state = map_emotion(dominant_emotion)
            except Exception:
                state = "No Face Detected"

            # Draw rectangle around detected face
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

        emotion_counter[state] += 1

        # Overlay the state
        cv2.putText(frame, f"State: {state}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Encode frame
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start')
def start():
    global cap, running
    if not running:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            return "Error: Camera not accessible", 500
        running = True
    return "Started"

@app.route('/stop')
def stop():
    global cap, running
    if running:
        running = False
        if cap:
            cap.release()
            cap = None
    return "Stopped"

@app.route('/video_feed')
def video_feed():
    if running and cap:
        return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
    return "Camera not running"

@app.route('/emotion_data')
def emotion_data():
    return jsonify(dict(emotion_counter))

if __name__ == "__main__":
    app.run(debug=True)
