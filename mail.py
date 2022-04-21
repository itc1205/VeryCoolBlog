from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

PASSWORD = "unknown"
EMAIL = "m21899339@gmail.com"

def sendEmail(email, text="Example text"):

    message = text

    msg = MIMEMultipart()
    msg["From"] = EMAIL
    msg["To"] = email
    msg["Subject"] = "Subscription"

    msg.attach(MIMEText(message, 'plain'))


    server = smtplib.SMTP('smtp.gmail.com: 587')

    server.starttls()

    server.login(msg["From"], PASSWORD)


    server.sendmail(msg["From"], msg["To"], msg.as_string())

    server.quit()

if __name__ == "__main__":
    sendEmail()