import base64
import json
import unittest
import datetime
from src import create_app, mongo
from tests.integrated.configs import MONGO_TEST_URI


class TestRevendedor(unittest.TestCase):
    _HEADERS = {"Content-Type": "application/json"}

    def setUp(self):
        self.app = create_app(MONGO_TEST_URI)
        self.app = self.app.test_client()
        self.revendedor_collection = mongo.db.get_collection('revendedor')
        self.token_collection = mongo.db.get_collection('token')

    def tearDown(self):
        for collection in mongo.db.list_collection_names():
            mongo.db.drop_collection(collection)

    def test_login__usuario_senha_correta__expected_token(self):
        # FIXTURES
        cpf = '67976752006'
        revendedor = {'cpf': cpf, 'nome': 'João Silva', 'senha': 'b'*12, 'email': 'teste@teste.com'}
        self.revendedor_collection.insert_one(revendedor)
        token = 'lkjdsfjsad09asd09as8d09ajsfkdjs0'
        self.token_collection.insert_one({'cpf': cpf, 'token': token, 'created_ad': datetime.datetime.now()})

        payload = {'cpf': cpf, 'senha': base64.b64encode(b'b'*12).decode()}

        # EXERCISE
        response = self.app.post('api/v1/revendedor/login', data=json.dumps(payload), headers=self._HEADERS)

        # ASSERTS
        self.assertEqual(200, response.status_code)
        body = response.json
        self.assertEqual(token, body['token'])

