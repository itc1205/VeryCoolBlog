from flask import Flask, render_template, redirect



app = Flask(__name__)
app.config['SECRET_KEY'] = 'literally_any_secret_key_but_go_onandtrytohackit*imsurethatthis-isprettyeas1y doаblе*'


def main():
    app.run()


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == "__main__":
    main()