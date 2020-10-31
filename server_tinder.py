from flask import Flask, jsonify, request

app = Flask(__name__)

pessoas = []
interesses = {}
matches = {}


@app.route('/pessoas', methods=['GET'])
def lista():
    return jsonify(pessoas)


@app.route('/pessoas', methods=['POST'])
def adiciona():
    pessoas.append(request.json)
    interesses[request.json['id']] = []
    matches[request.json['id']] = []
    return jsonify({'status': 'ok'})


@app.route('/pessoas/<int:id_pessoa>', methods=['GET'])
def busca_id(id_pessoa):
    for pessoa in pessoas:
        if pessoa['id'] == id_pessoa:
            return jsonify(pessoa)
    return jsonify({'erro': 'pessoa não encontrada'}), 404


@app.route('/reseta', methods=['POST'])
def reset():
    global pessoas, interesses, matches
    pessoas = []
    interesses = {}
    matches = {}
    return jsonify(pessoas)


@app.route('/interesses/<int:pessoa>', methods=['GET'])
def listainteresses(pessoa):
    if pessoa in interesses:
        return jsonify(interesses[pessoa])
    return jsonify({'erro': 'pessoa não encontrada'}), 404


@app.route('/sinalizar_interesse/<int:pessoa1>/<int:pessoa2>/',
           methods=['PUT'])
def sinalizar(pessoa1, pessoa2):
    if (pessoa1 in interesses) and (pessoa2 in interesses):

        for pessoa in pessoas:
            if pessoa['id'] == pessoa1:
                pessoa1 = pessoa
            if pessoa['id'] == pessoa2:
                pessoa2 = pessoa

        try:
            if pessoa2['sexo'] in pessoa1['buscando']:
                interesses[pessoa1['id']].append(pessoa2['id'])
            else:
                return jsonify({'erro': 'interesse incompativel'}), 400
        except KeyError:
            interesses[pessoa1['id']].append(pessoa2['id'])

        if (
           (pessoa1['id'] in interesses[pessoa2['id']]) and (
               (pessoa2['id'] in interesses[pessoa1['id']]))
           ):
            matches[pessoa1['id']].append(pessoa2['id'])
            matches[pessoa2['id']].append(pessoa1['id'])

        return jsonify(interesses)
    return jsonify({'erro': 'uma pessoa não existe'}), 404


@app.route('/sinalizar_interesse/<int:pessoa1>/<int:pessoa2>/',
           methods=['DELETE'])
def retirarinteresse(pessoa1, pessoa2):
    if (pessoa1 in interesses) and (pessoa2 in interesses):
        match1 = pessoa1 in interesses[pessoa2]
        match2 = pessoa2 in interesses[pessoa1]
        interesses[pessoa1].remove(pessoa2)

        if (match1 and match2):
            matches[pessoa1].remove(pessoa2)
            matches[pessoa2].remove(pessoa1)

        return jsonify(interesses)
    return jsonify({'erro': 'uma das pessoas não existe'}), 404


@app.route('/matches/<int:pessoa>', methods=['GET'])
def retmatches(pessoa):
    if pessoa in matches:
        return jsonify(matches[pessoa])
    return jsonify({'erro': 'uma das pessoas não existe'}), 404


if __name__ == '__main__':
    app.run(host='localhost', port=5003, debug=True)
