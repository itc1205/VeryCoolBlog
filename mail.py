import email.message
import smtplib

PASSWORD = "gonnaihbcridqcmc"
EMAIL = "s3rver.1@yandex.ru"
LOGIN = "s3rver.1"
server = smtplib.SMTP_SSL('smtp.yandex.ru', 465)

def startMailServer():
    server.login(LOGIN, PASSWORD)


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