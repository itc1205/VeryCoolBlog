from main import app, mail, db_session

if __name__ == "__main__":
    db_session.global_init("db/mainDB.sqlite")
    mail.startMailServer()
    app.run(host='0.0.0.0', port=80)
    mail.stopMailServer()