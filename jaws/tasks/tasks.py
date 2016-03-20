from celery import Celery, chord
from celery.task.http import URL
from urllib.parse import urlencode
import requests
from tinydb import TinyDB, Query
db = TinyDB('../db/db.json')
Data = Query()


class Config(object):
    CELERY_IMPORTS = ('celery.task.http', 'jaws.tasks.tasks')  # Note: http://docs.celeryproject.org/en/latest/userguide/tasks.html#automatic-naming-and-relative-imports
    CELERY_RESULT_BACKEND = 'redis://localhost'
    BROKER_URL = 'amqp://guest@localhost'
    CELERY_ACCEPT_CONTENT = ['json', 'pickle']
    CELERY_DISABLE_RATE_LIMITS = True


app = Celery('tasks')
app.config_from_object(Config)


@app.task
def model1(data):
    data.update({'model1': 1})
    return data

@app.task
def model2(data):
    data.update({'model2': 2})
    return data

@app.task
def meta_model(data):
    inputs = data['meta_model_input']
    result = sum(inputs)/len(inputs)
    data['data'] = result
    return data

@app.task
def update_ws(data):
    """ data sent to the websocket (ws) must have the keys: 'ws_id' and 'data' """
    requests.post('http://127.0.0.1:8888/api/', json=data)
    return data

@app.task
def party_a(data):
    resp = requests.get('http://127.0.0.1:8002/api/a/?user_id=1')
    data.update({'party_a' : resp.json()})
    return data

@app.task
def party_b(data):
    resp = requests.get('http://127.0.0.1:8002/api/b/?user_id=1')
    data.update({'party_b' : resp.json()})
    return data

@app.task
def party_c(data):
    resp = requests.get('http://127.0.0.1:8002/api/c/?user_id=1')
    data.update({'party_c' : resp.json()})
    return data

@app.task
def agg_submodels(data_list, run_id, ws_id):
    """
    Aggregator to combine the submodels
    #TODO: deal with more than just model1
    #TODO: abstract the submodel outputs to be generic
    """
    data = {'run_id': run_id, 'ws_id': ws_id}
    meta_model_input = []
    for resp in data_list:
        meta_model_input.append(resp['model1'])
    data['meta_model_input'] = meta_model_input
    return data


@app.task
def run_async_flow(data):
    
    run_id = data['run_id']
    ws_id  = data['ws_id']

    header = [((party_a.s(data) | update_ws.s()) |
               (model1.s()      | update_ws.s())),
              ((party_b.s(data) | update_ws.s()) |
               (model1.s()      | update_ws.s())),
              ((party_c.s(data) | update_ws.s()) |
               (model1.s()      | update_ws.s()))]
    
    callback = (agg_submodels.s(run_id=run_id, ws_id=ws_id) | meta_model.s() | update_ws.s())

    res = chord(header)(callback)

    # res = chord([
    #         party_a.subtask(kwargs={'ws_id':ws_id}, options={'link':model1.subtask(kwargs={'ws_id':ws_id})}),
    #         party_b.subtask(kwargs={'ws_id':ws_id}, options={'link':model1.subtask(kwargs={'ws_id':ws_id})}),
    #         party_c.subtask(kwargs={'ws_id':ws_id}, options={'link':model1.subtask(kwargs={'ws_id':ws_id})})
    #       ])(agg_submodels.subtask(options={'link':meta_model.subtask(kwargs={'ws_id':ws_id})}))
 
    return 'running get_third_parties'




# mex = chord([model1.s(1,1), model2.s(2,2)])(meta_model.s())
