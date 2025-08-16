import cv2
import face_recognition
import os
import smbus
from gpiozero import Servo
import smtplib
import datetime
from time import sleep

# Servo setup: adjust GPIO pins if needed
pan_servo = Servo(17)
tilt_servo = Servo(18)

# UPS HAT settings (example Geekworm, change address/register for your HAT)
I2C_ADDR = 0x36
bus = smbus.SMBus(1)

def read_battery_voltage():
    data = bus.read_word_data(I2C_ADDR, 2)
    voltage = ((data & 0xff) << 8 | (data >> 8)) * 1.25 / 1000 / 16
    return voltage

def read_battery_percent():
    data = bus.read_word_data(I2C_ADDR, 4)
    percent = ((data & 0xff) << 8 | (data >> 8)) / 256
    return percent

# Email notification settings
EMAIL_ADDRESS = 'your_email@gmail.com'
EMAIL_PASSWORD = 'your_app_password'
TO_EMAIL = 'recipient_email@gmail.com'

def send_email_alert(subject, body, attachment=None):
    import email, ssl
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.mime.base import MIMEBase
    from email import encoders

    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = TO_EMAIL
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    if attachment and os.path.exists(attachment):
        with open(attachment, "rb") as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(attachment)}')
        msg.attach(part)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as server:
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)

def map_servo(value, frame_size, servo_range=(-1, 1)):
    position = (value / frame_size) * (servo_range[1] - servo_range[0]) + servo_range[0]
    return max(min(position, servo_range[1]), servo_range[0])

# Load known faces
known_face_encodings = []
known_face_names = []
for filename in os.listdir('known_faces'):
    image = face_recognition.load_image_file(f"known_faces/{filename}")
    encoding = face_recognition.face_encodings(image)[0]
    known_face_encodings.append(encoding)
    known_face_names.append(os.path.splitext(filename)[0])

video_capture = cv2.VideoCapture(0)
ret, prev_frame = video_capture.read()
prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)

while True:
    ret, frame = video_capture.read()
    rgb_frame = frame[:, :, ::-1]
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    frame_height, frame_width = frame.shape[:2]

    # UPS HAT monitoring
    battery_voltage = read_battery_voltage()
    battery_percent = read_battery_percent()

    # Display battery info on frame
    cv2.putText(frame, f"UPS: {battery_voltage:.2f}V {battery_percent:.1f}%%", 
                (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

    # Motion Detection
    diff = cv2.absdiff(prev_gray, gray)
    thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)[1]
    motion_level = thresh.sum()
    if motion_level > 100000:
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        if not os.path.exists('events'):
            os.makedirs('events')
        event_file = f'events/motion_{timestamp}.jpg'
        cv2.imwrite(event_file, frame)
        send_email_alert('Motion Alert', f'Motion detected at {timestamp}', event_file)
    prev_gray = gray

    # Face Recognition & Tracking
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        name = "Unknown"
        if True in matches:
            first_match_index = matches.index(True)
            name = known_face_names[first_match_index]
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, .9, (255, 255, 255), 2)
        if name == "Unknown":
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            event_file = f'events/unknown_{timestamp}.jpg'
            cv2.imwrite(event_file, frame)
            send_email_alert('Unknown Person Alert', f'Unknown person detected at {timestamp}', event_file)
        # Camera Tracking
        face_center_x = (left + right) // 2
        face_center_y = (top + bottom) // 2
        pan_position = map_servo(face_center_x, frame_width)
        tilt_position = map_servo(face_center_y, frame_height)
        pan_servo.value = pan_position
        tilt_servo.value = tilt_position
        sleep(0.05)

    cv2.imshow('CCTV Monitoring', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video_capture.release()
cv2.destroyAllWindows();