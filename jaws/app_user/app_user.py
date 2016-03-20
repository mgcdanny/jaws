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
                    console.log(this.responseText)
                    userData = JSON.parse(this.responseText) // this.response is the server-side response
                    addTextNode('status', messageRecieve)
                    socket = new WebSocket('ws://127.0.0.1:8888/ws/' + socketID); // use socket variable from outer scope
                    socket.onopen = function (e) {
                        socket.send('hello, server, this is the the client');
                    }
                    socket.onmessage = function (event) {
                        console.log('socket on');
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
    # TODO (asynchronously):
        # respond the user a response saying 'thank you for your data'
        # send user data to app_external
        # send app_external responses to app_models
        # update the user page with results from app_models when complete
    print('*'*50, flush=True)
    print(request.form, flush=True)
    session['user_input'] = request.form['user_input']
    run_id = db.insert(request.form) # run_id must be unique inorder to also use as celery task_id
    res = tasks.run_async_flow.apply_async((request.form['socketID'],), task_id=str(run_id))
    return jsonify({'run_id': run_id})

if __name__ == '__main__':
    app.run('127.0.0.1', 8000, debug=True)
