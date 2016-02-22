from flask import Flask, jsonify
app = Flask(__name__)

@app.route('/api/model/a', methods=['POST'])
def model1():
    #TODO: take the value from sum('api/a', user_data)
    api = 0 
    result = sum(api, request.json['user_data'])
    return jsonify({'model': result})

@app.route('/api/model/b', methods=['POST'])
def model2():
    #TODO: take the value from sum('api/b', user_data)
    api = 0 
    result = sum(api, request.json['user_data'])
    return jsonify({'model': result})

@app.route('/api/model/c', methods=['POST'])
def model3():
    # TODO: model/c  waits for both model/a and model/b to complete
    # sum(model/a, model/b
    modelA = 0
    modelB = 0
    res = sum(modelA, modelB)
    return jsonify({'model': result})

if __name__ == '__main__':
    app.run('127.0.0.1', 8001, debug=False)
