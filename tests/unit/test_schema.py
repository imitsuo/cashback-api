import unittest
from src.schema import RevendedorSchema


class RevendedorSchemaTest(unittest.TestCase):

    def test_validate__representante_valido__nenhum_erro(self):
        revendedor = RevendedorSchema().load(
            {"cpf": "87535514600", "nome": "Um Nome Qualquer", "senha": "senha!234aaaaaa", "email": "teste@teste.com"}
        )

        self.assertEqual('87535514600', revendedor.cpf)
        self.assertEqual('Um Nome Qualquer', revendedor.nome)
        self.assertEqual('senha!234', revendedor.senha)
        self.assertEqual('teste@teste.com', revendedor.email)

    def test_validate__cpf_invalido__cpf_invalido(self):
        errors = RevendedorSchema().validate(
            {'cpf': '12345', 'nome': 'qualquer nome', 'senha': 'senha!234', 'email': 'teste@teste.com'}
        )

        self.assertEqual(1, len(errors))
        self.assertEqual(['Cpf inválido.'], errors['cpf'])

    def test_validate__nome_nao_informado__nome_obrigatorio(self):
        errors = RevendedorSchema().validate(
            {'cpf': '87535514600', 'nome': '', 'senha': 'senha!234', 'email': 'teste@teste.com'}
        )

        self.assertEqual(1, len(errors))
        self.assertEqual(['Nome deve ter no mínimo 2 e no máximo 100 caracteres.'], errors['nome'])

    def test_validate__nome_menor_que_2_caracteres__nome_invalido(self):
        errors = RevendedorSchema().validate(
            {'cpf': '87535514600', 'nome': 'a', 'senha': 'senha!234', 'email': 'teste@teste.com'}
        )

        self.assertEqual(1, len(errors))
        self.assertEqual(['Nome deve ter no mínimo 2 e no máximo 100 caracteres.'], errors['nome'])

    def test_validate__nome_maior_que_100_caracteres__nome_invalido(self):
        errors = RevendedorSchema().validate(
            {'cpf': '87535514600', 'nome': 'a' * 101, 'senha': 'senha!234', 'email': 'teste@teste.com'}
        )

        self.assertEqual(1, len(errors))
        self.assertEqual(['Nome deve ter no mínimo 2 e no máximo 100 caracteres.'], errors['nome'])

    def test_validate__senha_nao_informa__senha_obrigatorio(self):
        errors = RevendedorSchema().validate(
            {'cpf': '87535514600', 'nome': 'Um Nome Qualquer', 'senha': '', 'email': 'teste@teste.com'}
        )

        self.assertEqual(1, len(errors))
        self.assertEqual(['Senha deve ter no mínimo 8 e no máximo 10 caracteres.'], errors['senha'])

    def test_validate__senha_menor_que_8_caracteres__senha_invalida(self):
        errors = RevendedorSchema().validate(
            {'cpf': '87535514600', 'nome': 'Um Nome Qualquer', 'senha': 'a', 'email': 'teste@teste.com'}
        )

        self.assertEqual(1, len(errors))
        self.assertEqual(['Senha deve ter no mínimo 8 e no máximo 10 caracteres.'], errors['senha'])

    def test_validate__senha_maior_que_10_caracteres__senha_invalida(self):
        errors = RevendedorSchema().validate(
            {'cpf': '87535514600', 'nome': 'Um Nome Qualquer', 'senha': 'a'*11, 'email': 'teste@teste.com'}
        )

        self.assertEqual(1, len(errors))
        self.assertEqual(['Senha deve ter no mínimo 8 e no máximo 10 caracteres.'], errors['senha'])