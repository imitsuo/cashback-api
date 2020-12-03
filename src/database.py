from pymongo import MongoClient
from src.config import MONGO_URI, DATABASE_NAME

def init_database():
    _client = MongoClient(MONGO_URI, connect=True)

    _database = _client[DATABASE_NAME]

    if not 'revendedor-pre-aprovado' in _database.list_collection_names():
        _database.create_collection('revendedor-pre-aprovado')
        _collection = _database.get_collection('revendedor-pre-aprovado')
        _collection.create_index('cpf', unique=True)

    revendedor_pre_aprovado_collection = _database['revendedor-pre-aprovado']

    revendedores_pre_aprovados = ['15350946056']
    for revendedor in revendedores_pre_aprovados:
        if not revendedor_pre_aprovado_collection.find_one({'cpf': revendedor}):
            revendedor_pre_aprovado_collection.insert_one({'cpf': revendedor})

    if not 'token' in _database.list_collection_names():
        _database.create_collection('token')
        _token_collection = _database.get_collection('token')
        _token_collection.create_index('created_at', expireAfterSeconds=3600*24)

    if not 'revendedor' in _database.list_collection_names():
        _database.create_collection('revendedor')
        _collection = _database.get_collection('revendedor')
        _collection.create_index('cpf', unique=True)


if __name__ == '__main__':
    init_database()
