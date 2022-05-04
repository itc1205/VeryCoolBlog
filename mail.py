import email.message
import smtplib

PASSWORD = "2kfduNa7KcEAVMs"
EMAIL = "m21899339@gmail.com"
UNSUB_LINK = ""
SERVER_LINK = ""
server = smtplib.SMTP('smtp.gmail.com: 587')

server.starttls()

server.login(EMAIL, PASSWORD)

def sendEmail(mail, html="Example text"):

    msg = email.message.Message()
    msg["From"] = EMAIL
    msg["To"] = mail
    msg["Subject"] = "Subscription"

    msg.add_header('Content-Type', 'text/html')
    msg.set_payload(html)

    server.sendmail(msg["From"], msg["To"], msg.as_string())

def stopMailServer():
    server.quit()

if __name__ == "__main__":
    sendEmail()