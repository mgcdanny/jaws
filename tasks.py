from celery import Celery, chord
from celery.task.http import URL
from urllib.parse import urlencode

class Config(object):
    CELERY_IMPORTS = ('celery.task.http', )
    CELERY_RESULT_BACKEND = 'redis://localhost'
    BROKER_URL = 'amqp://guest@localhost'
    # CELERY_ACCEPT_CONTENT = ['json', 'pickle']


app = Celery('tasks')
app.config_from_object(Config)

@app.task
def add(x, y):
    return x + y

@app.task
def model1(x, y):
    return x+y

@app.task
def model2(x, y):
    return x*y

@app.task
def meta_model(args):
    return sum(args)/len(args)

@app.task
def party_a(**kwargs):
    res = URL('http://127.0.0.1:8002/api/a/').get_async(**kwargs)
    return res

@app.task
def get_third_parties(user_id):
    header = URL('http://example.com/multiply')
    callback = None
    chord(header)(callback)


# mex = chord([model1.s(1,1), model2.s(2,2)])(meta_model.s())
