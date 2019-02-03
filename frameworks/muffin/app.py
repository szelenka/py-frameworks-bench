import os

import aiohttp
import muffin
import peewee


HTTP_HOST = os.environ.get('HTTP_HOST', '127.0.0.1:8080')
SQL_HOST = os.environ.get('SQL_HOST', '127.0.0.1:5432')

PEEWEE_CONNECTION = 'postgres+pool://benchmark:benchmark@%s/benchmark' % SQL_HOST
PEEWEE_CONNECTION_PARAMS = {'encoding': 'utf-8', 'max_connections': 10}
REMOTE_URL = 'http://%s' % HTTP_HOST

if os.environ.get('TEST'):
    PEEWEE_CONNECTION = 'sqlite:///:memory:'
    PEEWEE_CONNECTION_PARAMS = {}
    REMOTE_URL = 'http://google.com'


app = muffin.Application(
    'web',

    PLUGINS=('muffin_peewee', 'muffin_jinja2'),

    JINJA2_TEMPLATE_FOLDERS=os.path.dirname(os.path.abspath(__file__)),

    PEEWEE_CONNECTION=PEEWEE_CONNECTION,
    PEEWEE_CONNECTION_MANUAL=True,
    PEEWEE_CONNECTION_PARAMS=PEEWEE_CONNECTION_PARAMS,

)


@app.ps.peewee.register
class Message(peewee.Model):
    content = peewee.CharField(max_length=512)


@app.register('/json')
def json(request):
    return {
        'message': 'Hello, World!'
    }


@app.register('/remote')
def remote(request):
    response = yield from aiohttp.request('GET', REMOTE_URL) # noqa
    return response.text()


@app.register('/complete')
def message(request):
    with (yield from app.ps.peewee.manage()):
        messages = list(Message.select().order_by(peewee.fn.Random()).limit(100))
    messages.append(Message(content='Hello, World!'))
    messages.sort(key=lambda m: m.content)
    return app.ps.jinja2.render('template.html', messages=messages)
