from celery import Celery, chord
from celery.task.http import URL
from urllib.parse import urlencode
import requests


class Config(object):
    CELERY_IMPORTS = ('celery.task.http', 'jaws.tasks.tasks')  # Note: celery_imports needs to be aware of where the tasks are
    CELERY_RESULT_BACKEND = 'redis://localhost'
    BROKER_URL = 'amqp://guest@localhost'
    CELERY_ACCEPT_CONTENT = ['json', 'pickle']


app = Celery('tasks')
app.config_from_object(Config)


@app.task
def model1(data, ws_id):
    return 1

@app.task
def model2(data, ws_id):
    return 2

@app.task
def meta_model(data_list, ws_id):
    data = sum(data_list)/len(data_list)
    requests.post('http://127.0.0.1:8888/api/', json={'ws_id': ws_id, 'data': data}) # TODO: this post request should not be hardcoded here, probably should be a seperate task
    return 'meta model executed'


@app.task
def party_a(**kwargs):
    print(kwargs, flush=True)
    res = requests.get('http://127.0.0.1:8002/api/a/?user_id=1')
    data = res.json()
    data['source'] = 'party_a'
    requests.post('http://127.0.0.1:8888/api/', json={'ws_id': kwargs['ws_id'], 'data': data}) # TODO: this post request should not be hardcoded here, probably should be a seperate task
    return data

@app.task
def party_b(**kwargs):
    res = requests.get('http://127.0.0.1:8002/api/b/?user_id=1')
    data = res.json()
    data['source'] = 'party_b'
    requests.post('http://127.0.0.1:8888/api/', json={'ws_id': kwargs['ws_id'], 'data': data}) # TODO: this post request should not be hardcoded here, probably should be a seperate task
    return data

@app.task
def party_c(**kwargs):
    res = requests.get('http://127.0.0.1:8002/api/c/?user_id=1')
    data = res.json()
    data['source'] = 'party_c'
    requests.post('http://127.0.0.1:8888/api/', json={'ws_id': kwargs['ws_id'], 'data': data}) # TODO: this post request should not be hardcoded here, probably should be a seperate task
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
def run_async_flow(ws_id):
    res = chord([
            party_a.subtask(kwargs={'ws_id':ws_id}, options={'link':model1.subtask(kwargs={'ws_id':ws_id})}),
            party_b.subtask(kwargs={'ws_id':ws_id}, options={'link':model1.subtask(kwargs={'ws_id':ws_id})}),
            party_c.subtask(kwargs={'ws_id':ws_id}, options={'link':model1.subtask(kwargs={'ws_id':ws_id})})
          ])(agg_submodels.subtask(options={'link':meta_model.subtask(kwargs={'ws_id':ws_id})}))
    return 'running get_third_parties'


# mex = chord([model1.s(1,1), model2.s(2,2)])(meta_model.s())
