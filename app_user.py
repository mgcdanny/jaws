from flask import Flask, jsonify, request, redirect, url_for, session
from db import db, Data

app = Flask(__name__)

app.secret_key = '1 secret key this is !'

@app.route('/')
def home():
    return '''
    <!doctype html>
    <title>JAWS Demo</title>
    <h1>Enter User Data</h1>
    <form action='/api/user' method=post enctype=multipart/form-data>
      <h2>User ID</h2>
      <p><input type=text name=user_id>
      <h2>User Input</h2>
      <p><input type=text name=user_input>
      <p><input type=submit value=Submit>
    </form>
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
    print(request.form, flush=True)
    session['user_input'] = request.form['user_input']
    input_id = db.insert(request.form)
    print(input_id, flush=True)
    # trigger events on input_id
    return redirect(url_for('waiting'))

if __name__ == '__main__':
    app.run('127.0.0.1', 8000, debug=True)
