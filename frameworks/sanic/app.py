import os
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
import databases

from aiohttp import ClientSession

from sanic import Sanic, response
from marshmallow import Schema, fields


HTTP_HOST = os.environ.get('HTTP_HOST', '127.0.0.1:8000')
SQL_HOST = os.environ.get('SQL_HOST', '127.0.0.1')
DATABASE_URL = "postgresql://benchmark:benchmark@%s:5432/benchmark" % SQL_HOST

metadata = sa.schema.MetaData()
Base = declarative_base(metadata=metadata)


# Database table definitions.
class Message(Base):
    __tablename__ = 'message'
    id = sa.Column(sa.Integer, primary_key=True)
    content = sa.Column(sa.String(length=512))


class MessageSchema(Schema):
    id = fields.Int()
    content = fields.String()


schema = MessageSchema(many=True)

# Application setup.
database = databases.Database(DATABASE_URL)
app = Sanic(__name__)


@app.listener('before_server_start')
async def startup(sanic, loop):
    await database.connect()


@app.listener('after_server_stop')
async def shutdown(sanic, loop):
    await database.disconnect()


@app.route('/json')
async def json(req):
    return response.json(body='Hello, World!')


@app.route('/remote')
async def remote(req):
    url = 'http://%s' % HTTP_HOST
    async with ClientSession() as session:
        async with session.get(url) as r:
            text = await r.text()
            return response.html(text)


@app.route('/complete')
async def complete(req):
    stmt = Message.__table__.select().order_by(sa.func.random()).limit(100)
    messages = await database.fetch_all(stmt)
    messages.sort(key=lambda m: m['content'])

    return response.json(schema.dump(messages))


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=5000)
