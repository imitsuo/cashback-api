import uuid
from datetime import datetime
from dateutil.relativedelta import relativedelta
import requests
from src import mongo
from src.api.errors import ApiValidationError
from src.config import URL_CASHBACK_ACUMULADO, TOKEN_API_CASHBACK
from src.model import Revendedor, Compra, CompraCashBack
from src.schema import RevendedorSchema, CompraSchema


class RevendedorService:

    def __init__(self):
        self._revendedor_collection = mongo.db.get_collection('revendedor')
        self._token_collection = mongo.db.get_collection('token')

    def salvar(self, revendedor: Revendedor):
        _revendedor = self._revendedor_collection.find_one({'cpf': revendedor.cpf})
        if _revendedor:
            return
        _model = RevendedorSchema().dump(revendedor)
        self._revendedor_collection.insert_one(_model)

    def obter(self, cpf: str) -> Revendedor:
        if not cpf:
            return None
        result = self._revendedor_collection.find_one({'cpf': cpf})
        if result:
            return RevendedorSchema().load(result, unknown='EXCLUDE')
        return None

    def login(self, cpf: str, senha: str):
        revendedor = self._revendedor_collection.find_one({'cpf': cpf})

        if revendedor and revendedor.get('senha') == senha:
            token = self._token_collection.find_one({'cpf': cpf})
            if not token:
                token = {'cpf': cpf, 'token': uuid.uuid4(), 'created_at': datetime.now()}
                self._token_collection.insert_one(token)
            return True, token['token']

        return False, None


class CompraService:

    def __init__(self):
        self._revendedor_pre_aprovado_collection = mongo.db.get_collection('revendedor-pre-aprovado')
        self._compra_collection = mongo.db.get_collection('compra')
        self._revendedor_service = RevendedorService()

    def _validar_revendedor(self, cpf: str):
        _revendedor = self._revendedor_service.obter(cpf)
        if not _revendedor:
            raise ApiValidationError('O revendedor informado não foi encontrado.')
        return _revendedor

    def salvar(self, compra: Compra):
        self._validar_revendedor(compra.cpf_revendedor)

        _compra = self._compra_collection.find_one({'codigo': compra.codigo})
        if _compra:
            raise ApiValidationError('Compra já cadastrada.')

        _revendedor_pre_aprovado = self._revendedor_pre_aprovado_collection.find_one({'cpf': compra.cpf_revendedor})
        if _revendedor_pre_aprovado:
            _status = Compra.STATUS_APROVADO
        else:
            _status = Compra.STATUS_EM_VALIDACAO
        compra.status = _status

        _compra = CompraSchema().dump(compra)

        self._compra_collection.insert_one(CompraSchema().dump(compra))
        return compra

    def listar_paginado(self, cpf_revendedor: str, offset: int):

        total = self._compra_collection.find({'cpf_revendedor': cpf_revendedor}).count()
        result = self._compra_collection.find({'cpf_revendedor': cpf_revendedor}).skip(offset).limit(100)

        compras = CompraSchema().load(list(result), many=True, unknown='EXCLUDE')

        return {'total': total, 'compras': compras}

    def obter_percentual_cashback(self, cpf_revendedor: str, ano: int, mes: int):
        _data_inicio = datetime(ano, mes, 1)
        _data_fim = datetime(ano, mes, 1) + relativedelta(months=1)
        mongo_result = self._compra_collection.aggregate(
            [
                {'$match': {'$and': [
                    {'cpf_revendedor': cpf_revendedor},
                    {'data': {'$gte': _data_inicio.isoformat()}},
                    {'data': {'$lt': _data_fim.isoformat()}}
                ]}
                },
                {'$group': {'_id': '$cpf_revendedor', 'total': {'$sum': '$valor'}}}
            ]
        )

        result = list(mongo_result)
        if len(result) > 0:
            total = result[0]['total']
            if total <= 1000:
                return 10
            elif 1000 < total <= 1500:
                return 15
            elif total > 1500:
                return 20

        return 10

    def calcular_cashback(self, compras: [Compra]) -> [CompraCashBack]:
        dict_cashback = {}
        compras_cashback = []
        for compra in compras:
            ano_mes = f'{compra.data.year}{compra.data.month:02}'
            if not dict_cashback.get(ano_mes):
                percentual_cashback = self.obter_percentual_cashback(
                    compra.cpf_revendedor, compra.data.year, compra.data.month
                )
                dict_cashback[ano_mes] = percentual_cashback
            else:
                percentual_cashback = dict_cashback[ano_mes]

            _compracashback = CompraCashBack(
                codigo=compra.codigo,
                cpf_revendedor=compra.cpf_revendedor,
                valor=compra.valor,
                data=compra.data,
                status=compra.status,
                percentual_cashback=percentual_cashback,
                valor_cashback=round(compra.valor * (percentual_cashback / 100), 2)
            )

            compras_cashback.append(_compracashback)
        return compras_cashback

    def obter_cashback_acumulado(self, cpf_revendedor: str):
        self._validar_revendedor(cpf_revendedor)

        url = f'{URL_CASHBACK_ACUMULADO}?cpf={cpf_revendedor}'
        response = requests.get(url, headers={'token': TOKEN_API_CASHBACK})

        if response.ok:
            _response = response.json()
            _body = _response['body']
            return {'cpf': cpf_revendedor, 'saldo': _body['credit']}

        raise Exception('Erro ao obter cashback acumulado')
