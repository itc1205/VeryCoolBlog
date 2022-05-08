from main import app
from data import db_session
import mail

if __name__ == "__main__":
    db_session.global_init("mainDB.sqlite")
    mail.startMailServer()
    app.run(host='0.0.0.0', port=80)
    mail.stopMailServer()
