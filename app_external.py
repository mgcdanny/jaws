from flask import Flask, jsonify, request
app = Flask(__name__)


@app.route('/api/a/', methods=['GET'])
def a():
    print(request.args, flush=True)
    user_dict = {1:100, 2:200, 3:300, 4:400}
    resp = jsonify({'data': user_dict.get(request.args['user_id'])})
    print(resp, flush=True)
    return resp

@app.route('/api/b', methods=['POST'])
def b():
    user_dict = {1:10, 2:20, 3:30, 4:40}
    user_id = request.json['user_id']
    return jsonify({'data': user_dict.get('user_id')})

@app.route('/api/c', methods=['POST'])
def c():
    user_dict = {1:1, 2:2, 3:3, 4:4}
    user_id = request.json['user_id']
    return jsonify({'data': user_dict.get('user_id')})

if __name__ == '__main__':
    app.run('127.0.0.1', 8002, debug=True)
