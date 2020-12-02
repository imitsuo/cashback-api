import datetime
import unittest
from functools import wraps
from unittest.mock import patch, Mock

import src.domain.service
from src.domain.service import CompraService
from src.model import Revendedor, Compra, CompraCashBack


class CompraServiceTest(unittest.TestCase):

    def setUp(self):
        self.revendedor_collection_mock = Mock()
        self.revendedor_pre_aprovado_collection_mock = Mock()
        self.compra_collection_mock = Mock()
        self.revendedor_service_mock = Mock()

    def mock_objects(self, mongo_mock, revendedor_service):
        collections = {
            'revendedor': self.revendedor_collection_mock,
            'revendedor-pre-aprovado': self.revendedor_pre_aprovado_collection_mock,
            'compra': self.compra_collection_mock
        }

        def _get_collection(name):
            return collections[name]

        mongo_mock.db.get_collection.side_effect = _get_collection
        revendedor_service.return_value = self.revendedor_service_mock

    @patch.object(src.domain.service, 'RevendedorService')
    @patch.object(src.domain.service, 'mongo')
    def test_salvar__compra_nao_cadastrada__expected_salvar(self, mongo_mock, revendedor_service_mock):
        # FIXTURES
        self.mock_objects(mongo_mock, revendedor_service_mock)
        self.compra_collection_mock.find_one.return_value = None
        self.revendedor_pre_aprovado_collection_mock.find_one.return_value = None
        compra = Compra(codigo='333', cpf_revendedor='23232323', valor=22.1, data=datetime.datetime(2020, 1, 1))

        # EXERCISE
        service = CompraService()
        service.salvar(compra)

        # ASSERTS
        self.revendedor_service_mock.obter.assert_called_once_with('23232323')
        self.revendedor_pre_aprovado_collection_mock.find_one.assert_called_once_with({'cpf': '23232323'})
        self.compra_collection_mock.find_one.assert_called_once_with({'codigo': '333'})
        self.compra_collection_mock.insert_one.assert_called_once_with(
            {
                'codigo': '333',
                'cpf_revendedor': '23232323',
                'data': datetime.datetime(2020, 1, 1).isoformat(),
                'status': 'Em Validação',
                'valor': 22.1
            }
        )

    @patch.object(src.domain.service, 'RevendedorService')
    @patch.object(src.domain.service, 'mongo')
    def test_salvar__compra_nao_cadastrada_revendedor_pre_aprovado__expected_salvar(
            self, mongo_mock, revendedor_service_mock
    ):
        # FIXTURES
        self.mock_objects(mongo_mock, revendedor_service_mock)
        self.compra_collection_mock.find_one.return_value = None
        compra = Compra(codigo='333', cpf_revendedor='23232323', valor=22.1, data=datetime.datetime(2020, 1, 1))

        # EXERCISE
        service = CompraService()
        service.salvar(compra)

        # ASSERTS
        self.revendedor_service_mock.obter.assert_called_once_with('23232323')
        self.revendedor_pre_aprovado_collection_mock.find_one.assert_called_once_with({'cpf': '23232323'})
        self.compra_collection_mock.find_one.assert_called_once_with({'codigo': '333'})
        self.compra_collection_mock.insert_one.assert_called_once_with(
            {
                'codigo': '333',
                'cpf_revendedor': '23232323',
                'data': datetime.datetime(2020, 1, 1).isoformat(),
                'status': 'Aprovado',
                'valor': 22.1
            }
        )

    @patch.object(src.domain.service, 'RevendedorService')
    @patch.object(src.domain.service, 'mongo')
    def test_salvar__compra_cadastrada__expected_exception(self, mongo_mock, revendedor_service_mock):
        # FIXTURES
        self.mock_objects(mongo_mock, revendedor_service_mock)
        self.revendedor_pre_aprovado_collection_mock.find_one.return_value = None
        compra = Compra(codigo='333', cpf_revendedor='23232323', valor=22.1, data=datetime.datetime(2020, 1, 1))

        # EXERCISE
        service = CompraService()

        with self.assertRaises(Exception):
            service.salvar(compra)

        # ASSERTS
        self.revendedor_service_mock.obter.assert_called_once_with('23232323')
        self.revendedor_pre_aprovado_collection_mock.assert_not_called()
        self.compra_collection_mock.find_one.assert_called_once_with({'codigo': '333'})
        self.compra_collection_mock.insert_one.assert_not_called()

    @patch.object(src.domain.service, 'RevendedorService')
    @patch.object(src.domain.service, 'mongo')
    def test_salvar__revendedor_nao_cadastrado__expected_exception(self, mongo_mock, revendedor_service_mock):
        # FIXTURES
        self.mock_objects(mongo_mock, revendedor_service_mock)
        self.revendedor_service_mock.obter.return_value = None
        compra = Compra(codigo='333', cpf_revendedor='23232323', valor=22.1, data=datetime.datetime(2020, 1, 1))

        # EXERCISE
        service = CompraService()

        with self.assertRaises(Exception):
            service.salvar(compra)

        # ASSERTS
        self.revendedor_service_mock.obter.assert_called_once_with('23232323')
        self.revendedor_pre_aprovado_collection_mock.assert_not_called()
        self.compra_collection_mock.find_one.assert_not_called()
        self.compra_collection_mock.insert_one.assert_not_called()

    @patch.object(src.domain.service, 'RevendedorService')
    @patch.object(src.domain.service, 'mongo')
    def test_obter_percentual_cashback__compras_menores_que_1000__expected_10_porcento(
            self, mongo_mock, revendedor_mock
    ):
        # FIXTURES
        self.mock_objects(mongo_mock, revendedor_mock)

        self.compra_collection_mock.aggregate.return_value = yield {'total', 999.99}
        cpf = '123123233'
        ano = 2020
        mes = 1

        # EXERCISE
        service = CompraService()
        result = service.obter_percentual_cashback(cpf, ano, mes)

        # ASSERTS
        self.assertEqual(10, result)
        self.compra_collection_mock.aggregate.assert_called_once_with([
                {'$match': {'$and': [
                    {'cpf_revendedor': cpf},
                    {'data': {'$gte': datetime.datetime(2020, 1, 1).isoformat()}},
                    {'data': {'$lt': datetime.datetime(2020, 2, 1).isoformat()}}
                ]}
                },
                {'$group': {'_id': '$cpf_revendedor', 'total': {'$sum': '$valor'}}}
            ])

    @patch.object(src.domain.service, 'RevendedorService')
    @patch.object(src.domain.service, 'mongo')
    def test_obter_percentual_cashback__compras_igual_1499__expected_15_porcento(
            self, mongo_mock, revendedor_mock
    ):
        # FIXTURES
        self.mock_objects(mongo_mock, revendedor_mock)

        self.compra_collection_mock.aggregate.return_value = yield {'total', 1499.99}
        cpf = '123123233'
        ano = 2020
        mes = 1

        # EXERCISE
        service = CompraService()
        result = service.obter_percentual_cashback(cpf, ano, mes)

        # ASSERTS
        self.assertEqual(15, result)
        self.compra_collection_mock.aggregate.assert_called_once_with([
                {'$match': {'$and': [
                    {'cpf_revendedor': cpf},
                    {'data': {'$gte': datetime.datetime(2020, 1, 1).isoformat()}},
                    {'data': {'$lt': datetime.datetime(2020, 2, 1).isoformat()}}
                ]}
                },
                {'$group': {'_id': '$cpf_revendedor', 'total': {'$sum': '$valor'}}}
            ])


    @patch.object(src.domain.service, 'RevendedorService')
    @patch.object(src.domain.service, 'mongo')
    def test_obter_percentual_cashback__compras_igual_1501__expected_20_porcento(
            self, mongo_mock, revendedor_mock
    ):
        # FIXTURES
        self.mock_objects(mongo_mock, revendedor_mock)

        self.compra_collection_mock.aggregate.return_value = yield {'total', 1501.00}
        cpf = '123123233'
        ano = 2020
        mes = 1

        # EXERCISE
        service = CompraService()
        result = service.obter_percentual_cashback(cpf, ano, mes)

        # ASSERTS
        self.assertEqual(20, result)
        self.compra_collection_mock.aggregate.assert_called_once_with([
            {'$match': {'$and': [
                {'cpf_revendedor': cpf},
                {'data': {'$gte': datetime.datetime(2020, 1, 1).isoformat()}},
                {'data': {'$lt': datetime.datetime(2020, 2, 1).isoformat()}}
            ]}
            },
            {'$group': {'_id': '$cpf_revendedor', 'total': {'$sum': '$valor'}}}
        ])

    @patch.object(src.domain.service, 'RevendedorService')
    @patch.object(src.domain.service, 'mongo')
    def test_calcular_cashback__compra_cashback_15_procento__expected_cashback_15_porcento(
            self, mongo_mock, revendedor_mock
    ):
        # FIXTURES
        self.mock_objects(mongo_mock, revendedor_mock)

        self.compra_collection_mock.aggregate.return_value = yield {'total', 1501.00}
        cpf = '30672391643'
        compra = Compra(codigo='333', cpf_revendedor=cpf, valor=22.1, data=datetime.datetime(2020, 1, 15))

        # EXERCISE
        service = CompraService()
        result = service.calcular_cashback([compra])

        # ASSERTS
        self.assertIsNotNone(result)
        self.assertEqual(
            [
                CompraCashBack(
                    codigo=compra.codigo,
                    cpf_revendedor=compra.cpf_revendedor,
                    valor=compra.valor,
                    data=compra.data,
                    status=compra.status,
                    percentual_cashback=20,
                    valor_cashback=4.42
                )
            ],
            result)

    @patch.object(src.domain.service, 'requests')
    @patch.object(src.domain.service, 'RevendedorService')
    @patch.object(src.domain.service, 'mongo')
    def test_obter_cashback_acumulado__cashback_compras__expected_cashback(
            self, mongo_mock, revendedor_mock, requests_mock
    ):
        # FIXTURES
        self.mock_objects(mongo_mock, revendedor_mock)
        response_mock = Mock()
        response_mock.json.return_value = {'body': {'credit': 999999.98}}
        requests_mock.get.return_value = response_mock

        # EXERCISE
        service = CompraService()
        result = service.obter_cashback_acumulado('23423434343')

        # ASSERTS
        self.assertEqual({'cpf': '23423434343', 'saldo': 999999.98}, result)
