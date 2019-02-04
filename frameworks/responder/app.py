import asyncio
import asyncpg
import os
import responder
import requests
import jinja2
from random import randint
from operator import itemgetter

from sqlalchemy import create_engine, schema, Column
from sqlalchemy.sql.expression import func
from sqlalchemy.types import Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

HTTP_HOST = os.environ.get('HTTP_HOST', '127.0.0.1:8080')
SQL_HOST = os.environ.get('SQL_HOST', '127.0.0.1')

engine = create_engine("postgres://benchmark:benchmark@%s:5432/benchmark" % SQL_HOST, pool_size=10)
metadata = schema.MetaData()
Base = declarative_base(metadata=metadata)
Session = sessionmaker(bind=engine)


class Message(Base):
    __tablename__ = 'message'

    id = Column(Integer, primary_key=True)
    content = Column(String(length=512))


async def setup_database():
    global connection_pool
    connection_pool = await asyncpg.create_pool(
        user=os.getenv('PGUSER', 'benchmark'),
        password=os.getenv('PGPASS', 'benchmark'),
        database='benchmark',
        host=SQL_HOST,
        port=5432
    )


def load_fortunes_template():
    path = os.path.join('template.html')
    with open(path, 'r') as template_file:
        template_text = template_file.read()
        return jinja2.Template(template_text)


connection_pool = None
sort_fortunes_key = itemgetter(1)
template = load_fortunes_template()
loop = asyncio.get_event_loop()
loop.run_until_complete(setup_database())


app = responder.API()


@app.route('/json')
def json_serialization(req, resp):
    resp.media = {'message': 'Hello, world!'}


@app.route('/remote')
def remote(req, resp):
    response = requests.get('http://%s' % HTTP_HOST)
    resp.text = response.text


@app.route('/complete')
async def complete(req, resp):
    messages = list(Message.query.order_by(func.random()).limit(100))
    messages.append(Message(content='Hello, World!'))
    messages.sort(key=lambda m: m.content)
    resp.headers['Content-Type'] = "text/html;charset=utf-8"
    resp.content = template.render(messages=messages)


if __name__ == '__main__':
    app.run('0.0.0.0')
