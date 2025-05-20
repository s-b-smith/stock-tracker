import smtplib
import sys
from email.mime.text import MIMEText
from stock_secrets import google_email_address, google_app_password
from utils import printn

def send_email_to_myself(message: str, subject: str) -> None:
    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = google_email_address
    msg['To'] = google_email_address

    try:
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.login(google_email_address, google_app_password)
        s.sendmail(google_email_address, google_email_address, msg.as_string())
        printn("Email sent successfully!")
    except Exception as e:
        printn(f"Error sending email: {e}")
    finally:
        s.quit()

if __name__ == "__main__":
    message = sys.argv[1]

    send_email_to_myself(message, "TEST")