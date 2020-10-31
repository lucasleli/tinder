from flask import Flask, jsonify, request

app = Flask(__name__)

pessoas = []
interesses = {}

@app.route('/pessoas', methods=['GET'])
def lista():
    return jsonify(pessoas)


@app.route('/pessoas', methods=['POST'])
def adiciona():
    pessoas.append(request.json)
    interesses[request.json['id']] = []
    return jsonify({'status':'ok'})


@app.route('/pessoas/<int:id_pessoa>', methods=['GET'])
def busca_id(id_pessoa):
    for pessoa in pessoas:
        if pessoa['id'] == id_pessoa:
            return jsonify(pessoa)
    return jsonify({'erro': 'pessoa não encontrada'}), 404


@app.route('/reseta', methods=['POST'])
def reset():
    global pessoas, interesses
    pessoas = []
    interesses = {}
    return jsonify(pessoas)


@app.route('/interesses/<int:pessoa>', methods=['GET'])
def listainteresses(pessoa):
    if pessoa in interesses:
        return jsonify(interesses[pessoa])
    return jsonify({'erro': 'pessoa não encontrada'}), 404


@app.route('/sinalizar_interesse/<int:pessoa1>/<int:pessoa2>/', methods=['PUT'])
def sinalizar(pessoa1, pessoa2):
    if (pessoa1 in interesses) and (pessoa2 in interesses):
        interesses[pessoa1].append(pessoa2)
        return jsonify(interesses)
    return jsonify({'erro': 'uma das pessoas não existe'}), 404


if __name__ == '__main__':
    app.run(host = 'localhost', port = 5003, debug = True)