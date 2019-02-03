import json
import os

import requests
from sqlalchemy import create_engine, schema, Column, Integer, String
from sqlalchemy.sql.expression import func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from jinja2 import Template


TEMPLATE = Template(open(os.path.join(os.path.dirname(__file__), 'template.html')).read())

HTTP_HOST = os.environ.get('HTTP_HOST', '127.0.0.1:8080')
SQL_HOST = os.environ.get('SQL_HOST', '127.0.0.1:5432')

engine = create_engine("postgres://benchmark:benchmark@%s/benchmark" % SQL_HOST, pool_size=10)
metadata = schema.MetaData()
Base = declarative_base(metadata=metadata)
Session = sessionmaker(bind=engine)


class Message(Base):
    __tablename__ = 'message'

    id = Column(Integer, primary_key=True)
    content = Column(String(length=512))


def app(env, start_response):
    path = env['PATH_INFO']
    if path == '/json':
        start_response('200 OK', [('Content-Type', 'application/json')])
        return [json.dumps({'message': 'Hello, world!'}).encode('utf-8')]

    if path == '/remote':
        start_response('200 OK', [('Content-Type', 'text/html')])
        remote = requests.get('http://%s' % HTTP_HOST).text
        return [remote.encode('utf-8')]

    if path == '/complete':
        start_response('200 OK', [('Content-Type', 'text/html')])
        session = Session()
        messages = list(session.query(Message).order_by(func.random()).limit(100))
        messages.append(Message(content='Hello, World!'))
        messages.sort(key=lambda m: m.content)
        session.close()
        return [TEMPLATE.render(messages=messages).encode('utf-8')]

    start_response('404 Not Found', [('Content-Type', 'text/plain')])
    return [b'Not Found']
