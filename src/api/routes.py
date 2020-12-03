import base64
import json

from flask import request, Response
from . import api_bp, validate_request_json
from .errors import ApiValidationError
from ..domain.service import CompraService, RevendedorService
from ..schema import CompraSchema, CompraCashBackSchema, RevendedorSchema


@api_bp.route('/revendedor/<string:cpf>/compra', methods=['POST'])
@validate_request_json()
def adcionar_compra(cpf: str):
    payload = request.json

    errors = CompraSchema().validate(payload)
    if errors:
        return Response(json.dumps(errors), status=400, mimetype='application/json')

    if cpf != payload['cpf_revendedor']:
        raise ApiValidationError('Cpf informado na rota diferente do payload')

    _compra = CompraSchema().load(payload)
    _compra = CompraService().salvar(_compra)
    return Response(CompraSchema().dumps(_compra), status=201, mimetype='application/json')


@api_bp.route('/revendedor/<string:cpf>/compras', methods=['GET'])
def listar(cpf: str):
    offset = request.args.get('offset')
    if not offset:
        offset = 0
    else:
        offset = int(offset)

    service = CompraService()
    result = service.listar_paginado(cpf, offset)
    compras_cashback = service.calcular_cashback(result['compras'])
    response = {'compras': CompraCashBackSchema().dump(compras_cashback, many=True), 'total': result['total']}

    return Response(json.dumps(response), status=200, mimetype='application/json')


@api_bp.route('/revendedor/', methods=['POST'])
@validate_request_json()
def create():
    payload = request.json
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

    if not payload.get('cpf') or not payload.get('senha'):
        raise ApiValidationError('Informe cpf e senha no request')

    cpf = payload['cpf']
    senha = payload['senha']
    senha = base64.b64decode(senha).decode()

    result, token = RevendedorService().login(cpf, senha)

    if result:
        return Response(json.dumps({'token': token}), 200, mimetype='application/json')

    return Response('', 401, mimetype='application/json')


@api_bp.route('/revendedor/<string:cpf>/cashback', methods=['GET'])
def obter_saldo_cashback(cpf: str):
    saldo = CompraService().obter_cashback_acumulado(cpf)
    return Response(json.dumps(saldo), 200, mimetype='application/json')
