from flask import Flask, jsonify, request

app = Flask(__name__)

pessoas = []


@app.route('/pessoas', methods=['GET'])
def lista():
    return jsonify(pessoas)


@app.route('/pessoas', methods=['POST'])
def adiciona():
    pessoas.append(request.json)
    return jsonify({'status':'ok'})


@app.route('/pessoas/<int:id_pessoa>', methods=['GET'])
def busca_id(id_pessoa):
    for pessoa in pessoas:
        if pessoa['id'] == id_pessoa:
            return jsonify(pessoa)
    return jsonify({'erro': 'pessoa não encontrada'}), 404


@app.route('/reseta', methods=['POST'])
def reset():
    global pessoas
    pessoas = []
    return jsonify(pessoas)


@app.route('/sinalizar_interesse/<int:pessoa1>/<int:pessoa2>', methods=['PUT'])
def sinalizar(pessoa1, pessoa2):
    pass

if __name__ == '__main__':
    app.run(host = 'localhost', port = 5003, debug = True)