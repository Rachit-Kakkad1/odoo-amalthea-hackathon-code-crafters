import os
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

# Load environment variables from your .env file
load_dotenv()

# --- SMTP Configuration (loaded from .env file) ---
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")

def send_login_notification_email(user: dict):
    """
    Sends a login notification email for admin or manager roles.
    This is a synchronous function and should be run in a background task in FastAPI.
    """
    # Ensure all required environment variables are present
    if not all([SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, RECIPIENT_EMAIL]):
        print("❌ SMTP settings are missing in the .env file. Cannot send email.")
        return

    # Create the email message
    msg = MIMEMultipart('alternative')
    msg['Subject'] = f"Login Alert: {user['role'].upper()} Logged In"
    msg['From'] = f"Expense Manager <{SMTP_USER}>"
    msg['To'] = RECIPIENT_EMAIL

    html_body = f"""
    <h3>Login Notification</h3>
    <p>A user with elevated privileges has just logged into the system.</p>
    <ul>
        <li><strong>User Email:</strong> {user['email']}</li>
        <li><strong>Role:</strong> {user['role']}</li>
        <li><strong>Login Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</li>
    </ul>
    """
    msg.attach(MIMEText(html_body, 'html'))

    try:
        print(f"Attempting to send notification to {RECIPIENT_EMAIL}...")
        # Using STARTTLS (port 587)
        if SMTP_PORT == 587:
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.send_message(msg)
        
        # Using SSL (port 465)
        elif SMTP_PORT == 465:
            with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.send_message(msg)
        else:
            print(f"Unsupported SMTP port {SMTP_PORT}. Email not sent.")
            return

        print(f"✅ Login notification email sent successfully for {user['email']}")

    except smtplib.SMTPAuthenticationError:
        print("\n❌ EMAIL AUTH FAILED: Check your SMTP_USER and SMTP_PASSWORD in the .env file.")
    except Exception as e:
        print(f"\n❌ An unexpected error occurred while sending email: {e}")