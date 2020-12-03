import json

from flask import request, Response
from . import api_bp, validate_request_json
from ..domain.service import CompraService
from ..schema import CompraSchema, CompraCashBackSchema

#TODO: Criar handler para validar se resquest é json e capturar erros e formatar response


@api_bp.route('/revendedor/<string:cpf>/compra', methods=['POST'])
@validate_request_json()
def adcionar_compra(cpf: str):
    payload = request.json

    errors = CompraSchema().validate(payload)
    if errors:
        return Response(json.dumps(errors), status=400, mimetype='application/json')

    if cpf != payload['cpf_revendedor']:
        raise Exception('Cpf informado na rota diferente do payload')

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
