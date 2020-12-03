import json
import base64
import requests
from flask import request, Response
from src.schema import RevendedorSchema
from src.domain.service import RevendedorService, CompraService

from . import api_bp, validate_request_json


@api_bp.route('/revendedor/', methods=['POST'])
@validate_request_json()
def create():
    payload = request.json
    errors = RevendedorSchema().validate(payload)

    if errors:
        return Response(json.dumps(errors), status=400, mimetype='application/json')

    revendedor = RevendedorSchema().load(payload)

    result = RevendedorService().obter(revendedor.cpf)
    if not result:
        RevendedorService().salvar(revendedor)
        return Response(json.dumps(payload), status=201, mimetype='application/json')

    return Response('Revendedor já cadastrado', status=400, mimetype='application/json')


@api_bp.route('/revendedor/login', methods=['POST'])
@validate_request_json()
def login():
    payload = request.json
    # TODO VALIDAR

    cpf = payload['cpf']
    senha = payload['senha']
    senha = base64.b64decode(senha).decode()

    result, token = RevendedorService().login(cpf, senha)

    if result:
        return Response({'token': token}, 200, mimetype='application/json')

    return Response('', 401, mimetype='application/json')


@api_bp.route('/revendedor/<string:cpf>/cashback', methods=['GET'])
def obter_saldo_cashback(cpf: str):
    saldo = CompraService().obter_cashback_acumulado(cpf)
    return Response(json.dumps(saldo), 200, mimetype='application/json')
