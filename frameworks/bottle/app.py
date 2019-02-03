# Database
import os

HTTP_HOST = os.environ.get('HTTP_HOST', '127.0.0.1:8080')
SQL_HOST = os.environ.get('SQL_HOST', '127.0.0.1:5432')

from sqlalchemy import create_engine, schema, Column
from sqlalchemy.sql.expression import func
from sqlalchemy.types import Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine("postgres://benchmark:benchmark@%s/benchmark" % SQL_HOST, pool_size=10)
metadata = schema.MetaData()
Base = declarative_base(metadata=metadata)
Session = sessionmaker(bind=engine)


class Message(Base):
    __tablename__ = 'message'

    id = Column(Integer, primary_key=True)
    content = Column(String(length=512))


# Application

import bottle
import requests

app = bottle.Bottle()


@app.route('/json')
def json():
    return {'message': 'Hello, World!'}


@app.route('/remote')
def remote():
    response = requests.get('http://%s' % HTTP_HOST)
    return response.text


@app.route('/complete')
def complete():
    session = Session()
    messages = list(session.query(Message).order_by(func.random()).limit(100))
    messages.append(Message(content='Hello, World!'))
    messages.sort(key=lambda m: m.content)
    session.close()
    return bottle.template('template', messages=messages)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

# pylama:ignore=E402
