import unittest
from unittest.mock import patch, Mock

from src.domain.service import RevendedorService

import src.domain.service
from src.domain.service import RevendedorService
from src.model import Revendedor


class RevendedorServiceTest(unittest.TestCase):

    def setUp(self):
        self.revendedor_collection_mock = Mock()
        self.token_collection_mock = Mock()

    def mock_collections(self, mongo_mock):
        collections = {'revendedor': self.revendedor_collection_mock, 'token': self.token_collection_mock}

        def _get_collection(name):
            return collections[name]

        mongo_mock.db.get_collection.side_effect = _get_collection

    @patch.object(src.domain.service, 'mongo')
    def test_salvar__revendedor_cadastrado__expected_nao_salvar(self, mongo_mock):
        # FIXTURES
        self.mock_collections(mongo_mock)
        revendedor = Revendedor(
            nome='Teste nome complente', cpf='70249837285', senha='Senhabonita', email='email@asd.com'
        )
        service = RevendedorService()

        # EXERCISE
        service.salvar(revendedor)

        # ASSERTS
        self.revendedor_collection_mock.find_one.assert_called_once_with({'cpf': '70249837285'})
        self.revendedor_collection_mock.insert_one.assert_not_called()

    @patch.object(src.domain.service, 'mongo')
    def test_salvar__revendedor_nao_cadastrado__expected_salvar(self, mongo_mock):
        # FIXTURES
        self.mock_collections(mongo_mock)
        self.revendedor_collection_mock.find_one.return_value = None
        revendedor = Revendedor(
            nome='Teste nome complente', cpf='70249837285', senha='Senhabonita', email='email@asd.com'
        )
        service = RevendedorService()

        # EXERCISE
        service.salvar(revendedor)

        # ASSERTS
        self.revendedor_collection_mock.find_one.assert_called_once_with({'cpf': '70249837285'})
        self.revendedor_collection_mock.insert_one.assert_called_once_with(
            {'nome': 'Teste nome complente', 'cpf': '70249837285', 'senha': 'Senhabonita', 'email': 'email@asd.com'}
        )

    @patch.object(src.domain.service, 'mongo')
    def test_obter__revendedor_cadastrado__expected_revendedor(self, mongo_mock):
        # FIXTURES
        self.mock_collections(mongo_mock)
        revendedor = {
            'nome': 'Teste nome complente', 'cpf': '70249837285', 'senha': 'Senhaboita', 'email': 'email@asd.com'
        }
        self.revendedor_collection_mock.find_one.return_value = revendedor
        service = RevendedorService()

        # EXERCISE
        result = service.obter('70249837285')

        # ASSERTS
        self.revendedor_collection_mock.find_one.assert_called_once_with({'cpf': '70249837285'})
        self.assertEqual(result.nome, revendedor['nome'])
        self.assertEqual(result.cpf, revendedor['cpf'])
        self.assertEqual(result.senha, revendedor['senha'])
        self.assertEqual(result.email, revendedor['email'])

    @patch.object(src.domain.service, 'mongo')
    def test_obter__revendedor_nao_cadastrado__expected_None(self, mongo_mock):
        # FIXTURES
        self.mock_collections(mongo_mock)
        self.revendedor_collection_mock.find_one.return_value = None
        service = RevendedorService()

        # EXERCISE
        result = service.obter('1231231231233')

        # ASSERTS
        self.revendedor_collection_mock.find_one.assert_called_once_with({'cpf': '1231231231233'})
        self.assertIsNone(result)

    @patch.object(src.domain.service, 'mongo')
    def test_login__senha_incorreta__expected_false(self, mongo_mock):
        # FIXTURES
        self.mock_collections(mongo_mock)
        revendedor = {
            'nome': 'Teste nome complente', 'cpf': '70249837285', 'senha': 'Senhaboita', 'email': 'email@asd.com'
        }
        self.revendedor_collection_mock.find_one.return_value = revendedor
        service = RevendedorService()

        # EXERCISE
        result, token = service.login('70249837285', 'asd')

        # ASSERTS
        self.revendedor_collection_mock.find_one.assert_called_once_with({'cpf': '70249837285'})
        self.assertFalse(result)
        self.assertIsNone(token)

    @patch.object(src.domain.service, 'mongo')
    def test_login__senha_correta_sem_token__expected_true_criar_token(self, mongo_mock):
        # FIXTURES
        self.mock_collections(mongo_mock)
        revendedor = {
            'nome': 'Teste nome complente', 'cpf': '70249837285', 'senha': 'Senhaboita', 'email': 'email@asd.com'
        }
        self.revendedor_collection_mock.find_one.return_value = revendedor
        self.token_collection_mock.find_one.return_value = None

        service = RevendedorService()

        # EXERCISE
        result, token = service.login('70249837285', 'Senhaboita')

        # ASSERTS
        self.revendedor_collection_mock.find_one.assert_called_once_with({'cpf': '70249837285'})
        self.token_collection_mock.insert_one.assert_called_once()
        self.assertTrue(result)
        self.assertIsNotNone(token)

    @patch.object(src.domain.service, 'mongo')
    def test_login__senha_correta_token_cadastrado__expected_true_token_cadastrado(self, mongo_mock):
        # FIXTURES
        self.mock_collections(mongo_mock)
        revendedor = {
            'nome': 'Teste nome complente', 'cpf': '70249837285', 'senha': 'Senhaboita', 'email': 'email@asd.com'
        }
        self.revendedor_collection_mock.find_one.return_value = revendedor
        self.token_collection_mock.find_one.return_value = {'cpf': '70249837285', 'token': 'asdjhalksjdalksjd'}

        service = RevendedorService()

        # EXERCISE
        result, token = service.login('70249837285', 'Senhaboita')

        # ASSERTS
        self.revendedor_collection_mock.find_one.assert_called_once_with({'cpf': '70249837285'})
        self.token_collection_mock.insert_one.assert_not_called()
        self.assertTrue(result)
        self.assertEqual('asdjhalksjdalksjd', token)

    @patch.object(src.domain.service, 'mongo')
    def test_login__revendedor_nao_cadastrado__expected_false(self, mongo_mock):
        # FIXTURES
        self.mock_collections(mongo_mock)
        self.revendedor_collection_mock.find_one.return_value = None
        service = RevendedorService()

        # EXERCISE
        result, token = service.login('70249837285', 'asd')

        # ASSERTS
        self.revendedor_collection_mock.find_one.assert_called_once_with({'cpf': '70249837285'})
        self.assertFalse(result)
        self.assertIsNone(token)
