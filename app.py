import time
from flask import Flask, Response

app = Flask(__name__)


def event_stream():
    count = 0
    while True:
        count += 1
        yield "data: %s\n\n" % count
        time.sleep(1)


@app.route("/")
def index():
    return Response(event_stream(), content_type="text/event-stream")


@app.route("/hello")
def hello_world():
    return "Hello, World! \n"


if __name__ == "__main__":
    app.run(debug=True, threaded=True, port=5000)
