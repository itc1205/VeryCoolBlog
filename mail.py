import email.message
import smtplib

PASSWORD = "2kfduNa7KcEAVMs"
EMAIL = "m21899339@gmail.com"
UNSUB_LINK = ""
SERVER_LINK = ""
server = smtplib.SMTP('smtp.gmail.com: 587')
failure_counter = 0

def startMailServer():
    server.starttls()
    server.login(EMAIL, PASSWORD)

def sendEmail(mail, html="Example text"):
    try:
        msg = email.message.EmailMessage()
        msg["From"] = EMAIL
        msg["To"] = mail
        msg["Subject"] = "Subscription"

        msg.add_header('Content-Type', 'text/html')
        msg.set_payload(html, "utf-8")

        server.sendmail(msg["From"], msg["To"], msg.as_string().encode())
    
    except:
        startMailServer()
        server.sendmail(msg["From"], msg["To"], msg.as_string().encode())


def stopMailServer():
    server.quit()

if __name__ == "__main__":
    sendEmail()
    stopMailServer()