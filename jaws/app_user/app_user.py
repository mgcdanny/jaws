from flask import Flask, jsonify, request, redirect, url_for, session
from jaws.tasks import tasks
from tinydb import TinyDB, Query

db = TinyDB('../db/db.json')
Data = Query()


app = Flask(__name__)

app.secret_key = '1 secret key this is !'


@app.route('/')
def home():
    return '''
    <!doctype html>
    <html>
        <head>
            <meta http-equiv="Content-Type" charset="UTF-8" />
            <script type="text/javascript">
                "use strict";

                var socket =  null; // init a socket variable
                var socketID = Math.random();
                var userData = null;

                var addTextNode = function(id, text){
                    // wrapper function to add text to existing html elements via id
                    var newContent = document.createTextNode(text);
                    var currentDiv = document.getElementById(id);
                    currentDiv.appendChild(newContent);
                };

                var messageRecieve = 'Information Recieved. Please Wait For Results :)'

                function ajaxSuccess () {
                    userData = JSON.parse(this.responseText) // this.responseText is the server-side response
                    addTextNode('status', messageRecieve)
                    socket = new WebSocket('ws://127.0.0.1:8888/ws/' + socketID); // use socket variable from outer scope
                    socket.onopen = function (e) {
                        socket.send('hello, server, this is the the client: ' + socketID);
                    }
                    socket.onmessage = function (event) {
                        console.log('socket onmessage');
                        console.log(event.data);
                        addTextNode('result', event.data)
                    }
                }

                function AJAXSubmit (oFormElement) {
                    var oFormElement = document.getElementById('userData')
                    var oReq = new XMLHttpRequest();
                    oReq.onload = ajaxSuccess;
                    oReq.open('POST', '/api/user');
                    var form = new FormData(oFormElement);
                    form.append('socketID', socketID);
                    console.log(form)
                    oReq.send(form);
                }
            </script>
        </head>
        <title>JAWS Demo</title>
        <h1>Enter User Data</h1>
        <form id='userData' method='post' enctype='multipart/form-data' onsubmit='AJAXSubmit(this); return false;'>
          <h2>User ID</h2>
          <p><input type=text name=user_id>
          <h2>User Input</h2>
          <p><input type=text name=user_input>
          <p><input type=submit value=Submit>

        </form>
        <div id='status'></div>
        <div id='result'></div>
    </html> 
    '''

@app.route('/waiting')
def waiting():
    return '''
    <!doctype html>
    <title>JAWS Demo</title>
    <h1>You submitted {}</h1>
    <h1>Awaiting for analysis ....</h1>
    '''.format(session['user_input'])

@app.route('/api/user', methods=['POST'])
def user():
    print(request.form, flush=True)
    data = request.form.copy()
    print(data, flush=True)
    run_id = db.insert(request.form) # run_id must be unique inorder to also use as celery task_id, easier to debug messages
    data['run_id'] = run_id
    data['ws_id'] = data['socketID']
    # todo: use sessions to keep track of all the runs a user might execute inorder to display on the website
    # session['user_input'] = data['user_input']
    res = tasks.run_async_flow.apply_async((data,), task_id=str(run_id))
    return jsonify({'data': data})

if __name__ == '__main__':
    app.run('127.0.0.1', 8000, debug=True)
