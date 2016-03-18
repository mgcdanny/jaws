from flask import Flask, jsonify, request
app = Flask(__name__)

@app.route('/api/a/', methods=['GET', 'POST'])
def a():
    user_dict = {1:100, 2:200, 3:300, 4:400}
    resp = jsonify({'data': user_dict.get(int(request.args['user_id']))})
    return resp

@app.route('/api/b/', methods=['GET', 'POST'])
def b():
    user_dict = {1:10, 2:20, 3:30, 4:40}
    resp = jsonify({'data': user_dict.get(int(request.args['user_id']))})
    return resp

@app.route('/api/c/', methods=['GET', 'POST'])
def c():
    user_dict = {1:1, 2:2, 3:3, 4:4}
    resp = jsonify({'data': user_dict.get(int(request.args['user_id']))})
    return resp


if __name__ == '__main__':
    app.run('127.0.0.1', 8002, debug=True)
