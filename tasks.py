from celery import Celery, chord
from celery.task.http import URL
from urllib.parse import urlencode
import requests

class Config(object):
    CELERY_IMPORTS = ('celery.task.http',)
    CELERY_RESULT_BACKEND = 'redis://localhost'
    BROKER_URL = 'amqp://guest@localhost'
    CELERY_ACCEPT_CONTENT = ['json', 'pickle']


app = Celery('tasks')
app.config_from_object(Config)


@app.task
def model1(data):
    return 1

@app.task
def model2(data):
    return 2

@app.task
def meta_model(args):
    return sum(args)/len(args)

@app.task
def party_a(**kwargs):
    res = requests.get('http://127.0.0.1:8002/api/a/?user_id=1')
    data = res.json()
    data['source'] = 'party_a'
    return data

@app.task
def party_b(**kwargs):
    res = requests.get('http://127.0.0.1:8002/api/b/?user_id=1')
    data = res.json()
    data['source'] = 'party_b'
    return data

@app.task
def party_c(**kwargs):
    res = requests.get('http://127.0.0.1:8002/api/c/?user_id=1')
    data = res.json()
    data['source'] = 'party_c'
    return data

@app.task
def agg_submodels(data_list):
    """
    Aggregator to combine the submodels
    """
    responses = []
    for resp in data_list:
        responses.append(resp['data'])
    # todo: kick off another celery task to run the meta_model
    return responses


@app.task
def run_async_flow(run_id):
    res = chord([
            party_a.subtask(kwargs={'_id':run_id}, options={'link':model1.s()}),
            party_b.subtask(kwargs={'_id':run_id}, options={'link':model1.s()}),
            party_c.subtask(kwargs={'_id':run_id}, options={'link':model1.s()})
          ])(agg_submodels.subtask(options={'link':meta_model.s()}))
    return 'running get_third_parties'


# mex = chord([model1.s(1,1), model2.s(2,2)])(meta_model.s())
