import os
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
import databases

from aiohttp import ClientSession

from quart import Quart, jsonify
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
app = Quart(__name__)



@app.before_serving
async def startup():
    await database.connect()


@app.after_serving
async def shutdown():
    await database.disconnect()


# Endpoints.
@app.route('/json')
async def json_serialization():
    return jsonify({'message': 'Hello, world!'})


@app.route('/remote')
async def remote():
    url = 'http://%s' % HTTP_HOST
    async with ClientSession() as session:
        async with session.get(url) as response:
            response = await response.text()
            return response


@app.route('/complete')
async def complete():
    stmt = Message.__table__.select().order_by(sa.func.random()).limit(100)
    messages = await database.fetch_all(stmt)
    messages.sort(key=lambda m: m['content'])

    return jsonify(schema.dump(messages))


if __name__ == "__main__":
    app.run()
