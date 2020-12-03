import json
import unittest
import datetime
from src import create_app, mongo
from tests.integrated.configs import MONGO_TEST_URI


class TestCompra(unittest.TestCase):
    _HEADERS = {"Content-Type": "application/json"}

    def setUp(self):
        self.app = create_app(MONGO_TEST_URI)
        self.app = self.app.test_client()
        self.revendedor_collection = mongo.db.get_collection('revendedor')
        self.compra_collection = mongo.db.get_collection('compra')

    def tearDown(self):
        for collection in mongo.db.list_collection_names():
            mongo.db.drop_collection(collection)

    def test_listar__compras_com_cashback__expected_compras_com_cashback(self):
        # FIXTURES
        cpf = '67976752006'
        revendedor = {'cpf': cpf, 'nome': 'João Silva', 'senha': 'b'*10, 'email': 'teste@teste.com'}
        self.revendedor_collection.insert_one(revendedor)

        self.compra_collection.insert_many([
            {'codigo': '101', 'valor': 1.1, 'cpf_revendedor': cpf, 'data': datetime.datetime(2020, 1, 10).isoformat()},
            {'codigo': '102', 'valor': 3.2, 'cpf_revendedor': cpf, 'data': datetime.datetime(2020, 1, 11).isoformat()},
        ])

        # EXERCISE
        response = self.app.get('api/v1/revendedor/67976752006/compras?offset=0')

        # ASSERTS
        self.assertEqual(200, response.status_code)
        self.assertEqual(
            {'compras': [
                {
                    'data': '2020-01-10T00:00:00',
                    'cpf_revendedor': '67976752006',
                    'valor_cashback': 0.11,
                    'valor': 1.1,
                    'codigo': '101',
                    'status': 'Em Validação',
                    'percentual_cashback': 10
                },
                {
                    'data': '2020-01-11T00:00:00',
                    'cpf_revendedor': '67976752006',
                    'valor_cashback': 0.32,
                    'valor': 3.2,
                    'codigo': '102',
                    'status': 'Em Validação',
                    'percentual_cashback': 10
                }
            ],
                'total': 2
            },
            response.json)

    def test_adcionar_compra__compra_valida__expected_salvar_compra(self):
        # FIXTURES
        cpf = '86342733775'
        revendedor = {'cpf': cpf, 'nome': 'João Silva', 'senha': 'a'*10, 'email': 'teste@teste.com'}
        self.revendedor_collection.insert_one(revendedor)

        compra = {
            'codigo': '21', 'valor': 100, 'cpf_revendedor': cpf, 'data': datetime.datetime(2020, 1, 10).isoformat()
        }

        # EXERCISE
        result = self.app.post(f'api/v1/revendedor/{cpf}/compra', data=json.dumps(compra), headers=self._HEADERS)

        # ASSERTS
        self.assertEqual(201, result.status_code)
        self.assertEqual({
                            'codigo': '21',
                            'cpf_revendedor': '86342733775',
                            'data': '2020-01-10T00:00:00',
                            'status': 'Em Validação',
                            'valor': 100.0
                        }, result.json
        )

        _compra = self.compra_collection.find_one({'codigo': compra['codigo']})
        self.assertEqual(compra['valor'], _compra['valor'])
        self.assertEqual(compra['cpf_revendedor'], _compra['cpf_revendedor'])
        self.assertEqual(compra['data'], _compra['data'])
        self.assertEqual('Em Validação', _compra['status'])

    def test_obter_saldo_cashback__cashback_acumulado__expected_saldo_cashback(self):
        # FIXTURES
        cpf = '56635345477'
        revendedor = {'cpf': cpf, 'nome': 'João Silva', 'senha': 'a' * 10, 'email': 'teste@teste.com'}
        self.revendedor_collection.insert_one(revendedor)

        # EXERCISE
        result = self.app.get(f'api/v1/revendedor/{cpf}/cashback')

        # ASSERT
        self.assertEqual(200, result.status_code)
        _result = result.json
        self.assertEqual(cpf, _result['cpf'])
        self.assertGreaterEqual(_result['saldo'], 0)
