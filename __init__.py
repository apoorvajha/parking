#!/usr/bin/env python3

# Main flask app

from flask import Flask

DEBUG = True

app = Flask(__name__)

@app.route("/")
def index():
    return "got started"


@app.route("/get_text")
def get_text():
    pass


@app.route("/get_current_image")
def get_current_image():
    pass


@app.route("/reset_client")
def reset_client():
    pass


if __name__ == "__main__":
    app.run(debug=DEBUG)
