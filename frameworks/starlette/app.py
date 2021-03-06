import os
import uvicorn
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
import databases
from starlette.applications import Starlette
from starlette.config import Config
# from starlette.middleware.database import DatabaseMiddleware
from starlette.responses import JSONResponse, HTMLResponse
from marshmallow import Schema, fields
from aiohttp import ClientSession


# Configuration from environment variables or '.env' file.

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
app = Starlette(template_directory='templates')
# app.add_middleware(DatabaseMiddleware, database_url=DATABASE_URL)


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


# Endpoints.
@app.route('/json')
async def json_serialization(req):
    return JSONResponse({'message': 'Hello, world!'})


@app.route('/remote')
async def remote(req):
    url = 'http://%s' % HTTP_HOST
    async with ClientSession() as session:
        async with session.get(url) as response:
            response = await response.text()
            return HTMLResponse(response)


@app.route('/complete')
async def complete(req):
    stmt = Message.__table__.select().order_by(sa.func.random()).limit(100)
    messages = await database.fetch_all(stmt)
    messages.sort(key=lambda m: m['content'])

    # template = app.get_template('template.html')
    # content = template.render(messages=list(messages))
    # return HTMLResponse(content)

    return JSONResponse(schema.dump(messages))


if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=5000)
