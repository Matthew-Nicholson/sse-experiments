import time
import uuid
from flask import Flask, Response, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///messages.db"
db = SQLAlchemy(app)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(80), nullable=False)
    message = db.Column(db.String(120), nullable=False)


class MessageID(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), nullable=False, unique=True)
    message_id = db.Column(db.Integer, db.ForeignKey("message.id"), nullable=False)


with app.app_context():
    db.create_all()


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


@app.route("/message", methods=["POST", "GET"])
def message():
    if request.method == "POST":
        data = request.get_json()
        message = data["message"]
        author = data["author"]
        new_message = Message(author=author, message=message)
        db.session.add(new_message)
        db.session.commit()

        new_message_id = MessageID(uuid=str(uuid.uuid4()), message_id=new_message.id)
        db.session.add(new_message_id)
        db.session.commit()
        return "Success", 200
    else:
        messages = (
            db.session.query(Message, MessageID)
            .join(MessageID, Message.id == MessageID.message_id)
            .all()
        )
        return {
            "messages": [
                {
                    "id": message.MessageID.id,
                    "author": message.Message.author,
                    "message": message.Message.message,
                    "uuid": message.MessageID.uuid,
                }
                for message in messages
            ]
        }, 200


if __name__ == "__main__":
    app.run(debug=True, threaded=True, port=5000)
