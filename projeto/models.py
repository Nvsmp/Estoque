from projeto import database, jsonify, datetime
from sqlalchemy import Enum

class Categoria(database.Model):
    id = database.Column(database.Integer, primary_key=True, autoincrement=True)
    nome = database.Column(database.String(99), nullable=False, unique=True)
    descricao = database.Column(database.String(99), nullable=False, unique=False)

    def to_dict(self):
        return {
            "id":self.id,
            "nome":self.nome,
            "descricao":self.descricao
        } 

class Fornecedor(database.Model):
    id = database.Column(database.Integer, primary_key=True, autoincrement=True)
    nome = database.Column(database.String(99), nullable=False, unique=True)
    cnpj = database.Column(database.String(18), nullable=False, unique=True)
    email = database.Column(database.String(99), nullable=False, unique=True)

    def to_dict(self):
        return {
            "id":self.id,
            "nome":self.nome,
            "cnpj":self.cnpj,
            "email":self.email
        } 

class Cliente(database.Model):
    id = database.Column(database.Integer, primary_key=True, autoincrement=True)
    nome = database.Column(database.String(99), nullable=False, unique=True)
    email = database.Column(database.String(99), nullable=False, unique=True)
    pjpf = database.Column(database.Enum("F", "J", name="name_documento", nullable=False, default="F"))
    documento = database.Column(database.String(18), nullable=False, unique=True)

class Usuario(database.Model):
    id = database.Column(database.Integer, primary_key=True, autoincrement=True)
    grupo = database.Column(Enum('GERENTE', 'FUNCIONARIO', name='name_grupo'), nullable=False, default='FUNCIONARIO')   
    email = database.Column(database.String(99), nullable=False, unique=True)
    username = database.Column(database.String(99), nullable=False, unique=True)
    passwd = database.Column(database.String(20), nullable=False)
    twofactorcode = database.Column(database.String(7), nullable=True, default="default")

class Produto(database.Model):
    id = database.Column(database.Integer, primary_key=True, autoincrement=True)
    nome = database.Column(database.String(99), nullable=False)
    quantidade = database.Column(database.Integer, nullable=True, default=0)
    descricao = database.Column(database.String(99), nullable=False, unique=False)
    deletado = database.Column(database.Boolean, default=False)
    id_fornecedor = database.Column(database.Integer, database.ForeignKey("fornecedor.id"), nullable=False)
    id_categoria = database.Column(database.Integer, database.ForeignKey("categoria.id"), nullable=False)


    def to_dict(self):
        return {
            "id":self.id,
            "nome":self.nome,
            "quantidade":self.quantidade
        } 

class Entrada(database.Model):
    id = database.Column(database.Integer, primary_key=True, autoincrement=True)
    id_usuario = database.Column(database.Integer, database.ForeignKey("usuario.id"), nullable=False)
    data = database.Column(database.DateTime, nullable=False, default=datetime.now())

class Saida(database.Model):
    id = database.Column(database.Integer, primary_key=True, autoincrement=True)
    id_usuario = database.Column(database.Integer, database.ForeignKey("usuario.id"), nullable=False)
    id_cliente = database.Column(database.Integer, database.ForeignKey("cliente.id"), nullable=False)
    data = database.Column(database.DateTime, nullable=False, default=datetime.now())

    def to_dict(self):
        return {
            "id":self.id,
            "id_usuario":self.id_usuario,
            "id_cliente":self.id_cliente,
            "data":self.data
        }

class Item(database.Model):
    id = database.Column(database.Integer, primary_key=True, autoincrement=True)
    id_produto = database.Column(database.Integer, database.ForeignKey("produto.id"), nullable=False)
    status = database.Column(Enum('ESTOQUE', 'VENDIDO'), nullable=False, name="name_status", default="ESTOQUE")
    valor_compra = database.Column(database.Numeric(10, 2), nullable=False)
    valor_venda = database.Column(database.Numeric(10, 2), nullable=True, default=0.00)
    id_entrada = database.Column(database.Integer, database.ForeignKey("entrada.id"), nullable=False)
    id_saida= database.Column(database.Integer, database.ForeignKey("saida.id"), nullable=True)

    def to_dict(self):
        return {
            "id":self.id,
            "status":self.status,
            "valor_venda":self.valor_venda,
            "valor_comprar":self.valor_compra,
            "id_produto":self.id_produto,
            "id_entrada":self.id_entrada,
            "id_saida":self.id_saida
        }
    