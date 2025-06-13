

# Create an email-sending function
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import smtplib


def send_email(to: str, subject: str, body: str) -> str:
    # Email configuration (replace with your SMTP server details)
    print("Sending email...")
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = os.getenv("GOOGLE_EMAIL")
    sender_password = os.getenv("GOOGLE_APP_PASSWORD")

    # Split the CSV string into a list of email addresses
    recipients = [email.strip() for email in to.split(",")]

    # Create the email message
    message = MIMEMultipart()
    message["From"] = sender_email
    # message["To"] = to_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    # Send the email
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        for recipient in recipients:
            message["To"] = recipient
            server.send_message(message)
            print(f"Email sent to {recipient} with subject: {subject}")
    
    print(f"Email sent to {to} with subject: {subject}")
    return f"Email sent to {to} with subject: {subject}"