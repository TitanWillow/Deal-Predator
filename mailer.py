import smtplib
from email.mime.text import MIMEText

smtp_server = "smtp.gmail.com"
port = 587  # For TLS
# Email details
def send_email(receiver_email):
    sender_email = "your_email@gmail.com"
    password = "your_password"  # Use an app password if applicable
    receiver_email = "recipient_email@gmail.com"

    # Create the email content
    subject = "Test Email"
    body = "This is a test email sent from Python."

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = receiver_email

    try:
        # Connect to the SMTP server and send the email
        with smtplib.SMTP(smtp_server, port) as server:
            server.starttls()  # Secure the connection
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")