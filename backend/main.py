import random
import time

import flask
from flask import request
from werkzeug.utils import secure_filename

app = flask.Flask(__name__)


@app.route("/")
def root():
    return flask.send_file("./index.html")


@app.route("/monkey.png")
def noan():
    time.sleep(random.randint(0, 10))
    return flask.send_file("./monkey.png")


@app.route("/upload/<filename>", methods=["POST"])
def up(filename: str):
    if request.method == "POST":
        if request.content_length > 1024:
            return flask.Response(
                "FILE TOO LARGE BOMBOCLAT!!! IT IS MORE THEN 1024 BYTES!!!! ME", 413
            )

        f = request.files["file"]
        f.save(f"./files/{secure_filename(filename)}")
        return flask.Response("k", 200)


@app.route("/upload-large/<filename>", methods=["POST"])
def uplarge(filename: str):
    if request.method == "POST":
        if request.content_length > 100000000000:
            flask.Response("too big", 400)

        f = request.files["file"]
        with open(f"./files/{secure_filename(filename)}", "ab") as file:
            file.write(f.stream.read())

        return flask.Response("k", 200)


@app.route("/files/<filename>")
def get_file(filename):
    return flask.send_from_directory("./files", filename)


def main():
    app.run("0.0.0.0", 3000)


if __name__ == '__main__':
    main()
