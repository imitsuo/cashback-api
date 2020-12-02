from datetime import datetime


class Revendedor:
    def __init__(self, nome: str, cpf: str, senha: str, email: str):
        self.nome = nome
        self.cpf = cpf
        self.senha = senha
        self.email = email


class Compra:
    STATUS_EM_VALIDACAO = 'Em Validação'
    STATUS_APROVADO = 'Aprovado'

    def __init__(self,
                 codigo: str,
                 cpf_revendedor: str,
                 valor: float,
                 data: datetime,
                 status: str = STATUS_EM_VALIDACAO
                 ):
        self.codigo = codigo
        self.cpf_revendedor = cpf_revendedor
        self.valor = valor
        self.data = data
        self.status = status


class CompraCashBack:
    def __init__(self,
                 codigo: str,
                 cpf_revendedor: str,
                 valor: float,
                 data: datetime,
                 status: str,
                 percentual_cashback: int,
                 valor_cashback: float
                 ):
        self.codigo = codigo
        self.cpf_revendedor = cpf_revendedor
        self.valor = valor
        self.data = data
        self.status = status
        self.percentual_cashback = percentual_cashback
        self.valor_cashback = valor_cashback

