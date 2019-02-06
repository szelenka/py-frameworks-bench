import asyncio
import asyncpg
import os
import uvicorn
import responder
import jinja2
# import gino
from aiohttp import ClientSession

HTTP_HOST = os.environ.get('HTTP_HOST', '127.0.0.1:8000')
SQL_HOST = os.environ.get('SQL_HOST', '127.0.0.1')

# sa = gino.Gino()
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base

metadata = sa.schema.MetaData()
Base = declarative_base(metadata=metadata)

class Message(Base):
    __tablename__ = 'message'

    id = sa.Column(sa.Integer, primary_key=True)
    content = sa.Column(sa.String(length=512))


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
# sort_fortunes_key = itemgetter(1)
template = load_fortunes_template()
loop = asyncio.get_event_loop()
loop.run_until_complete(setup_database())


app = responder.API()


@app.route('/json')
def json_serialization(req, resp):
    resp.media = {'message': 'Hello, world!'}


@app.route('/remote')
async def remote(req, resp):
    url = 'http://%s' % HTTP_HOST
    async with ClientSession() as session:
        async with session.get(url) as response:
            resp.text = await response.text()


@app.route('/complete')
async def complete(req, resp):
    # async with sa.with_bind("postgres://benchmark:benchmark@%s:5432/benchmark" % SQL_HOST) as engine:
    # async with sa.bind.acquire() as connection:
    async with connection_pool.acquire() as connection:
        messages = await connection.fetchall(Message.__table__.select().order_by(sa.func.random()).limit(100))

    messages.append(Message(content='Hello, World!'))
    messages.sort(key=lambda m: m.content)
    resp.headers['Content-Type'] = "text/html;charset=utf-8"
    resp.content = template.render(messages=list(messages))


if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=5000)
