import datetime
from marshmallow import Schema, fields, validate, validates, ValidationError, post_load
from src.model import Revendedor, Compra, CompraCashBack


class MyDateTimeField(fields.DateTime):
    def _deserialize(self, value, attr, data, **kwargs):
        if isinstance(value, datetime.datetime):
            return value
        return super()._deserialize(value, attr, data)


def _validate_cpf(value):
    #  Obtém os números do CPF e ignora outros caracteres
    cpf = [int(char) for char in value if char.isdigit()]

    #  Verifica se o CPF tem 11 dígitos
    if len(cpf) != 11:
        raise ValidationError("Cpf inválido.")

    #  Verifica se o CPF tem todos os números iguais, ex: 111.111.111-11
    #  Esses CPFs são considerados inválidos mas passam na validação dos dígitos
    #  Antigo código para referência: if all(cpf[i] == cpf[i+1] for i in range (0, len(cpf)-1))
    if cpf == cpf[::-1]:
        raise ValidationError("Cpf inválido.")

    #  Valida os dois dígitos verificadores
    for i in range(9, 11):
        value = sum((cpf[num] * ((i + 1) - num) for num in range(0, i)))
        digit = ((value * 10) % 11) % 10
        if digit != cpf[i]:
            raise ValidationError("Cpf inválido.")


class RevendedorSchema(Schema):
    nome = fields.Str(
        required=True,
        validate=validate.Length(
            min=2,
            max=100,
            error='Nome deve ter no mínimo {min} e no máximo {max} caracteres.'
        )
    )
    cpf = fields.Str(required=True)
    senha = fields.Str(
        required=True,
        validate=validate.Length(
            min=8,
            max=10,
            error='Senha deve ter no mínimo {min} e no máximo {max} caracteres.'
        )
    )
    email = fields.Str(required=True, validate=validate.Email())

    @post_load
    def make_revendedor(self, data: dict, **kwargs):
        return Revendedor(**data)

    # TODO: Conferir algoritmo
    @validates("cpf")
    def validate_cpf(self, value):
        _validate_cpf(value)


class CompraSchema(Schema):
    codigo = fields.Str(
                required=True,
                validate=validate.Length(min=1,
                                         max=50,
                                         error='Codigo deve ter no mínimo {min} e no máximo {max} caracteres.'
                                         )
    )
    cpf_revendedor = fields.Str(required=True)
    valor = fields.Float(required=True)
    data = fields.DateTime(required=True)
    status = fields.Str()

    @validates("cpf_revendedor")
    def validate_cpf(self, value):
        _validate_cpf(value)

    @validates("status")
    def validate_status(self, value):
        if value and value not in [Compra.STATUS_APROVADO, Compra.STATUS_EM_VALIDACAO]:
            raise ValidationError("Status inválido.")

    @post_load
    def make_compra(self, data: dict, **kwargs):
        return Compra(**data)


class CompraCashBackSchema(Schema):
    codigo = fields.Str()
    cpf_revendedor = fields.Str()
    valor = fields.Float()
    data = fields.DateTime()
    status = fields.Str()
    percentual_cashback = fields.Int()
    valor_cashback = fields.Float()

    @post_load
    def make_compra(self, data: dict, **kwargs):
        return CompraCashBack(**data)
