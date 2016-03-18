from celery import Celery, chord
from celery.task.http import URL
from urllib.parse import urlencode
import requests

class Config(object):
    CELERY_IMPORTS = ('celery.task.http',)
    CELERY_RESULT_BACKEND = 'redis://localhost'
    BROKER_URL = 'amqp://guest@localhost'
    # CELERY_ACCEPT_CONTENT = ['json', 'pickle']


app = Celery('tasks')
app.config_from_object(Config)


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
    print(data_list, flush=True)
    responses = {}
    for resp in data_list:
        responses[resp['source']] = resp['data']
    # todo: kick off another celery task to run the meta_model
    return responses

@app.task
def run_models(run_id):
    header = [model1.s(run_id), model2.s(run_id)]
    callback = meta_model.s()
    chord(header)(callback)
    return 'models running'

@app.task
def get_third_parties(run_id):
    res = chord([
            party_a.s(_id=run_id), #todo: link the submodel to run after the 3rd party data is recieved
            party_b.s(_id=run_id),
            party_c.s(_id=run_id)
          ])(agg_submodels.s())
    return 'running get_third_parties'


# mex = chord([model1.s(1,1), model2.s(2,2)])(meta_model.s())
