import os

HTTP_HOST = os.environ.get('HTTP_HOST', '127.0.0.1:8000')
SQL_HOST = os.environ.get('SQL_HOST', '127.0.0.1')

import flask
import requests
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import func
from marshmallow import Schema, fields


app = flask.Flask(__name__, template_folder='.')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://benchmark:benchmark@%s:5432/benchmark' % SQL_HOST
app.config['SQLALCHEMY_POOL_SIZE'] = 20
db = SQLAlchemy(app)


class Message(db.Model):
    __tablename__ = 'message'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(length=512))


class MessageSchema(Schema):
    id = fields.Int()
    content = fields.String()


schema = MessageSchema(many=True)


@app.route('/json')
def json():
    return flask.jsonify(message='Hello, World!')


@app.route('/remote')
def remote():
    response = requests.get('http://%s' % HTTP_HOST)
    return response.text


@app.route('/complete')
def complete():
    messages = list(Message.query.order_by(func.random()).limit(100))
    messages.append(Message(content='Hello, World!'))
    messages.sort(key=lambda m: m.content)
    # return flask.render_template('template.html', messages=messages)
    return flask.jsonify(schema.dump(messages))


if __name__ == '__main__':
    app.run('0.0.0.0')
