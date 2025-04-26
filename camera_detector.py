import smtplib
import ssl
import cv2
import pyautogui
import datetime
import random
import requests
import time
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# Gmail SMTP Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465  # SSL Port
GMAIL_USER = "your mail"
GMAIL_APP_PASSWORD = "your password "  # Use the 16-character App Password

# Email Details
EMAIL_TO = "thotakurayaswanth104@gmail.com"
EMAIL_SUBJECT = "🚨 Security Alert: Unauthorized Camera Detected!"

# Function to get public IP address
def get_public_ip():
    try:
        response = requests.get("https://api64.ipify.org?format=text")
        return response.text
    except requests.RequestException:
        return "Unable to fetch IP"

# Function to send email with attachments
def send_email(attachments):
    try:
        # Get device IP address
        device_ip = get_public_ip()

        # Email message setup
        msg = MIMEMultipart()
        msg["From"] = GMAIL_USER
        msg["To"] = EMAIL_TO
        msg["Subject"] = EMAIL_SUBJECT

        # Email body
        body = f"""
        🚨 **Security Alert!** 🚨
        Unauthorized camera access detected!
        
        📅 Date & Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        🌐 Device IP: {device_ip}
        
        📸 Attached images:
        - Screenshot of screen
        - Intruder's captured photo
        
        🔍 Please review the attached images for more details.
        """
        msg.attach(MIMEText(body, "plain"))

        # Attach only the valid images
        for file_path in attachments:
            if os.path.exists(file_path):
                with open(file_path, "rb") as attachment:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(attachment.read())
                    encoders.encode_base64(part)
                    part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(file_path)}")
                    msg.attach(part)

        # Send email using SMTP
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
            server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            server.sendmail(GMAIL_USER, EMAIL_TO, msg.as_string())

        print("✅ Email Alert Sent Successfully!")

    except Exception as e:
        print(f"❌ Failed to send email: {e}")

# Function to capture screenshot
def capture_screenshot():
    filename = f"screenshot_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    pyautogui.screenshot().save(filename)
    return filename

# Function to capture intruder photo
def capture_intruder_photo(frame):
    filename = f"intruder_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    cv2.imwrite(filename, frame)
    return filename

# Function to detect available cameras
def detect_cameras():
    available_cameras = []
    for i in range(5):  # Check up to 5 camera indexes
        cap = cv2.VideoCapture(i, cv2.CAP_MSMF)  # Use MSMF instead of DSHOW
        if cap.isOpened():
            available_cameras.append(i)
            cap.release()
        else:
            cap.release()
    return available_cameras

# Start Camera Monitoring
def monitor_cameras():
    print("🔍 Monitoring for unauthorized camera access...")

    while True:
        cameras = detect_cameras()

        if cameras:
            print(f"📷 Camera detected at index: {cameras}")

            # Open the first detected camera
            cap = cv2.VideoCapture(cameras[0], cv2.CAP_MSMF)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    # Capture evidence (ONLY detected camera photo + screenshot)
                    screenshot_path = capture_screenshot()
                    intruder_photo_path = capture_intruder_photo(frame)

                    # Send email alert with ONLY these images
                    send_email([screenshot_path, intruder_photo_path])

                cap.release()

        else:
            print("❌ No cameras detected. Monitoring continues...")

        # Wait for a random time (between 5 to 15 seconds) before checking again
        wait_time = random.randint(5, 15)
        print(f"⏳ Waiting {wait_time} seconds before next check...")
        time.sleep(wait_time)

# Run detection
if __name__ == "__main__":
    monitor_cameras()
