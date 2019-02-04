import os

HTTP_HOST = os.environ.get('HTTP_HOST', '127.0.0.1:8080')
SQL_HOST = os.environ.get('SQL_HOST', '127.0.0.1')

import requests
from weppy import App
from weppy.dal import DAL, Model, Field
from weppy.tools import service


app = App(__name__, template_folder='.')
app.config.db.uri = 'postgres://benchmark:benchmark@%s:5432/benchmark' % SQL_HOST

db = DAL(app, auto_migrate=False, pool_size=10)


class Message(Model):
    tablename = 'message'
    content = Field()

db.define_models(Message)


@app.route()
@service.json
def json():
    return dict(message='Hello, World!')


@app.route()
def remote():
    response = requests.get('http://%s' % HTTP_HOST)
    return response.text


@app.route(template='template.html', handlers=[db.handler])
def complete():
    messages = Message.all()
    messages = messages.select(paginate=(1, 100), orderby="random()")
    messages.append(Message.new(content='Hello, World!'))
    messages.sort(lambda m: m.content)
    return dict(messages=messages)

if __name__ == '__main__':
    app.run('0.0.0.0')
