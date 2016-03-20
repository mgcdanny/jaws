# https://github.com/hiroakis/tornado-websocket-example/blob/master/app.py
from tornado import websocket, web, ioloop
import json

wss = [] # websockets

class SocketHandler(websocket.WebSocketHandler):

    # javascript snippet to test:
    # socket = new WebSocket('ws://127.0.0.1:8888/ws/1');

    def check_origin(self, origin):
        return True

    def open(self, ws_id):
        print(ws_id)
        if self not in wss:
            self.ws_id = ws_id
            wss.append(self)

    def on_message(self, message):
        print(message)

    def on_close(self):
        if self in wss:
            wss.remove(self)

class ApiHandler(web.RequestHandler):
    # use this api to update the websockets from other servers

    @web.asynchronous
    def post(self, *args): # curl -X POST -d '{"ws_id":1}' 'http://127.0.0.1:8888/api/'
        self.finish() # what is this self.finish() do?
        data = json.loads(self.request.body.decode('utf-8'), encoding='utf-8')
        print(data)
        for ws in wss:
            if ws.ws_id == data['ws_id']:
                ws.write_message(json.dumps(data))


app = web.Application([
    (r'/api/', ApiHandler),
    (r'/ws/(?P<ws_id>.*)?', SocketHandler),
])

if __name__ == '__main__':
    app.listen(8888, '127.0.0.1')
    ioloop.IOLoop.instance().start()
