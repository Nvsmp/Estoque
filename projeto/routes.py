import random, string, json

from projeto import app, make_response, request, bcrypt, jsonify, database, create_access_token, jwt_required, get_jwt_identity, api, Resource, or_, current_user, datetime, jwt
from .models import Usuario, Produto, Item, Fornecedor, Categoria, Entrada, Saida, Cliente

@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return database.session.get(Usuario, identity) #Usuario.query.get(identity)

def att2f(id_usuario):
    with app.app_context():
        query = Usuario.query.filter_by(id=id_usuario).first()
        code = ''.join(random.choices(string.digits, k=7))
        query.twofactorcode = code
        database.session.commit()
        database.session.close()
        return code #DEBUG ONLYS

class Login(Resource):
    def get(self):
        try:
            # Endereço IP de origem (cliente)
            ip_origem = request.remote_addr
            # Endereço IP de destino (servidor Flask)
            ip_destino = request.host
            print(ip_origem, ip_destino)
            data = request.json
            usuario = Usuario.query.filter_by(email=data["email"]).first()
            if not usuario or not bcrypt.check_password_hash(usuario.passwd, data["pswd"]):
                return jsonify({ "msg":"Email/Senha Incorreto." }), 401  
            cod = att2f(usuario.id)
            response = make_response({"2f_token":f"{cod}"}, 200)
            response.headers["Content-Type"] = "application/json"
            return response
        except:
            return jsonify( {"msg":"Erro interno"} ), 500

class TwoFactor(Resource):
    def get(self):
        try:
            data = request.json 
            usuario = Usuario.query.filter_by(email=data.get("email")).first()
            if not usuario or not usuario.twofactorcode == data.get("2fc"):
                return jsonify( { "msg":"Email/Codigo Incorreto." } ), 401
            access_token = create_access_token(identity=usuario.id)
            response = make_response({"token":f"{access_token}"}, 200)
            response.headers["Content-Type"] = "application/json"
            return response
        except:
            return jsonify( {"msg":"Erro interno"} ), 500


class Home(Resource):
    @jwt_required()
    def get(self):
        return "IF THE POLICE CANT STOP YOU<br>YOU MUST BE ON<br><a href='https://youtu.be/LAoHCMu4xto?si=ZKLwMhpfUhMurP43'>THE DUST</a>", 200
    
class RotaCliente(Resource):
    @jwt_required()
    def post(self):
        try:
            data = request.json
            with app.app_context():
                if data["pjpf"] == "J":
                    novo_cliente = Cliente(nome=data["nome"], email=data["email"], pjpf="J", documento=data["documento"])
                else:
                    novo_cliente = Cliente(nome=data["nome"], email=data["email"], pjpf="F", documento=data["documento"])
                database.session.add(novo_cliente)
                database.session.commit()
                database.session.close()
            response = make_response({"msg":"Sucess"}, 200)
            response.headers["Content-Type"] = "application/json"
            response.headers["token"] = create_access_token(identity=get_jwt_identity())
            return response
        except:
            return jsonify( {"msg":"Erro interno"} ), 500
        
class RotaCategoria(Resource):
    @jwt_required()
    def get(self):
        try:
            data = request.json
            if not "id" or "nome" in data:
                return jsonify( {"msg":"Erro de parametros"} ), 422
            query = Categoria.query.filter( or_(Categoria.id == data["id"], Categoria.nome.ilike(f"%{data["nome"]}%")) ).first()
            if not query:
                return jsonify( {"msg":"Nenhum produto encontrado"} ), 404
            json = jsonify( query.to_dict() )
            response = make_response(json, 200)
            response.headers["Content-Type"] = "application/json"
            response.headers["token"] = create_access_token(identity=get_jwt_identity())
            return response
        except:
            return jsonify( {"msg":"Erro interno"} ), 500
    
    @jwt_required()
    def post(self):
        try:
            data = request.json
            if not "descricao" and "nome" in data:
                return jsonify( {"msg":"Erro de parametros"} ), 422
            query = Categoria.query.filter_by(nome=data["nome"]).first()
            if query:
                return jsonify( {"msg":"Ja Existente"} ), 422
            with app.app_context():
                database.session.add( Categoria(nome=data["nome"],descricao=data["descricao"]) )
                database.session.commit()
                database.session.close()
            response = make_response(jsonify({"msg":"Sucess"}), 200)
            response.headers["Content-Type"] = "application/json"
            response.headers["token"] = create_access_token(identity=get_jwt_identity())
            return response
        except:
            return jsonify( {"msg":"Erro interno"} ), 500
    
class RotaFornecedor(Resource):
    @jwt_required()
    def get(self):
        try:
            data = request.json
            if not "id" or "nome" in data:
                return jsonify( {"msg":"Erro de parametros"} ), 422
            query = Fornecedor.query.filter( or_(Fornecedor.id == data["id"], Fornecedor.nome.ilike(f"%{data["nome"]}%")) ).first()
            if not query:
                return jsonify( {"msg":"Nenhum fornecedor encontrado"} ), 404
            json = jsonify( query.to_dict() )
            response = make_response(json, 200)
            response.headers["Content-Type"] = "application/json"
            response.headers["token"] = create_access_token(identity=get_jwt_identity())
            return response
        except:
            return jsonify( {"msg":"Erro interno"} ), 500
    
    @jwt_required()
    def post(self):
        try:
            data = request.json
            query = Fornecedor.query.filter_by(nome=data["nome"]).first()
            if query:
                return jsonify( {"msg":"Ja Existente"} )
            with app.app_context():
                database.session.add( Fornecedor(nome=data["nome"],email=data["email"],cnpj=data["cnpj"]) )
                database.session.commit()
                database.session.close()
            resposta = make_response(jsonify({"msg":"Sucess"}), 200)
            resposta.headers["Content-Type"] = "application/json"
            resposta.headers["token"] = create_access_token(identity=get_jwt_identity())
            return resposta
        except:
            return jsonify( {"msg":"Erro interno"} ), 500

class RotaProduto(Resource):
    @jwt_required()
    def get(self):
        try:
            data = request.json
            if not "id" or "nome" in data:
                return jsonify( {"msg":"Erro de parametros"} ), 422
            query = Produto.query.filter( or_(Produto.id == data["id"], Produto.nome.ilike(f"%{data["nome"]}%")) ).first()
            if not query:
                return jsonify( {"msg":"Nenhum produto encontrado"} ), 404
            json = jsonify( query.to_dict() )
            response = make_response(json, 200)
            response.headers["Content-Type"] = "application/json"
            response.headers["token"] = create_access_token(identity=get_jwt_identity())
            return response
        except:
            return jsonify( {"msg":"Erro interno"} ), 500
    
    @jwt_required()
    def post(self): 
        try:
            data = request.json
            query = Produto.query.filter_by(nome=data["nome"]).first()
            if query:
                return jsonify( {"msg":"Produto ja cadastrado"} ) , 409
            with app.app_context():
                database.session.add( Produto(nome=data["nome"], descricao=data["descricao"], id_fornecedor=data["id_fornecedor"], id_categoria=data["id_categoria"]) )
                database.session.commit()
                database.session.close()
            resposta = make_response(jsonify({"msg":"Sucess"}), 200)
            resposta.headers["Content-Type"] = "application/json"
            resposta.headers["token"] = create_access_token(identity=get_jwt_identity())
            return resposta
        except:
            return jsonify( {"msg":"Erro interno"} ), 500
        
class RotaItem(Resource):
    @jwt_required()
    def get(self):
        try:
            data = request.json()
            query = Item.query.filter_by(id=data["id"]).first()
            if not query:
                return jsonify( {"msg":"Erro de parametros"} ), 422
            resposta = make_response(jsonify(query.to_dict()), 200)
            resposta.headers["Content-Type"] = "application/json"
            resposta.headers["token"] = create_access_token(identity=get_jwt_identity())
            return resposta
        except:
            return jsonify( {"msg":"Erro interno"} ), 500
    
    @jwt_required()
    def post(self):
        try:
            data = request.json
            usuario_atual = get_jwt_identity()
            nova_entrada = Entrada(id_usuario=current_user.id, data=datetime.now())
            database.session.add(nova_entrada)
            database.session.commit()
            for item in data["itens"]:
                print(f"ID_PRODUTO: {item['id_produto']}\nUSUARIO_ATUAL : {usuario_atual} \nVALOR_COMPRA: {item['valor_compra']}")
                query_produto = Produto.query.filter_by(id=item["id_produto"]).first()
                if not query_produto:
                    return jsonify( {"msg":"Nenhum produto encontrado"} ), 404
                query_produto.quantidade = int( query_produto.quantidade ) + 1
                database.session.add( Item( id_produto=item["id_produto"],valor_compra=item["valor_compra"], id_entrada=nova_entrada.id  ) )
                database.session.commit()
            database.session.close()

            resposta = make_response(jsonify({"msg":"Sucess"}), 200)
            resposta.headers["Content-Type"] = "application/json"
            resposta.headers["token"] = create_access_token(identity=get_jwt_identity())
            return resposta
        except:
            return jsonify( {"msg":"Erro interno"} ), 500
        
class RotaSaida(Resource):
    @jwt_required()
    def post(self):
        try:
            data = request.json
            usuario_atual = get_jwt_identity()
            print(usuario_atual)
            queryCliente = Cliente.query.filter_by(id=data["id_cliente"]).first()
            if not queryCliente:
                return jsonify( {"msg":"Erro de parametros"} ), 422
            with app.app_context():
                nova_saida = Saida(id_usuario=usuario_atual, id_cliente=queryCliente.id, data=datetime.now() )
                database.session.add(nova_saida)
                database.session.commit()
                print(data["itens"])
                for i in data["itens"]:
                    query = Item.query.filter_by(id=i).first()
                    if query:
                        query.status = "VENDIDO"
                        query.id_saida = nova_saida.id
                database.session.commit()     
            resposta = make_response(jsonify({"msg":"Sucess"}), 200)
            resposta.headers["Content-Type"] = "application/json"
            resposta.headers["token"] = create_access_token(identity=get_jwt_identity())
            return resposta
        except:
            return jsonify( {"msg":"Erro interno"} ), 500
        
    @jwt_required()
    def get(self):
        try: 
            data = request.json
            query = Saida.query.filter_by(id=data["id"]).first()
            if not query:
                return jsonify( {"msg":"Erro de parametros"} ), 422
            resposta = make_response(jsonify(query.to_dict()), 200)
            resposta.headers["Content-Type"] = "application/json"
            resposta.headers["token"] = create_access_token(identity=get_jwt_identity())
            return resposta
        except:
            return jsonify( {"msg":"Erro Interno"} ), 500
    
    


api.add_resource(Home,"/")
api.add_resource(Login,"/api/login")
api.add_resource(TwoFactor,"/api/2f")
api.add_resource(RotaCliente,"/api/Cliente")
api.add_resource(RotaCategoria,"/api/Categoria")
api.add_resource(RotaFornecedor,"/api/Fornecedor")
api.add_resource(RotaProduto,"/api/Produto")
api.add_resource(RotaItem,"/api/Item")
api.add_resource(RotaSaida,"/api/Saida")