import random, string, json

from projeto import send_file,sendEmail, app, make_response, request, bcrypt, jsonify, database, create_access_token, jwt_required, get_jwt_identity, api, Resource, or_, current_user, datetime, jwt, abort
from .models import * #Usuario, Produto, Item, Fornecedor, Categoria, Entrada, Saida, Cliente
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO

# ERRO DE TOKEN INVALIDO
@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({
        "msg": "Token inválido",
        "error": "invalid_token"
    }), 422

# ERRO DE TOKEN EXPIRADO
@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({
        "msg": "O token expirou",
        "error": "token_expired"
    }), 401

# GERAR NOTA FISCAL
def gerar_nota_fiscal_pdf(saida_id, cliente, itens):
    saida = Saida.query.filter_by(id=saida_id).first()
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    
    largura, altura = A4
    
    # Cabeçalho da Nota Fiscal
    c.setFont("Helvetica-Bold", 16)
    c.drawString(200, altura - 50, "NOTA FISCAL")
    
    # Informações da Saída e do Cliente
    c.setFont("Helvetica", 12)
    c.drawString(50, altura - 100, f"Nota Fiscal Nº: {saida.id}")
    c.drawString(50, altura - 120, f"Cliente: {cliente.nome}")
    c.drawString(50, altura - 140, f"Documento: {cliente.documento}")  # Adiciona o documento do cliente
    c.drawString(50, altura - 160, f"Data: {saida.data.strftime('%d/%m/%Y %H:%M')}")  # Data com horas e minutos
    
    # Tabela de Itens
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, altura - 200, "Produto")  # Coluna de Produto
    c.drawString(250, altura - 200, "Quantidade")  # Coluna de Quantidade
    c.drawString(400, altura - 200, "Preço Unitário")  # Coluna de Preço Unitário
    c.drawString(500, altura - 200, "Total")  # Coluna de Total
    
    c.line(50, altura - 205, 550, altura - 205)  # Linha divisória
    
    y = altura - 220  # Posição inicial dos itens
    total_nota = 0

    for i in itens:
        item = Item.query.filter_by(id=i).first()
        produto = Produto.query.filter_by(id=item.id_produto).first()
        quantidade = 1  # Supondo que cada item seja unitário
        preco_unitario = item.valor_venda
        total_item = quantidade * preco_unitario

        c.setFont("Helvetica", 12)
        c.drawString(50, y, produto.nome)  # Adiciona o nome do produto
        c.drawString(250, y, str(quantidade))  # Quantidade
        c.drawString(400, y, f"R$ {preco_unitario:.2f}")  # Preço unitário
        c.drawString(500, y, f"R$ {total_item:.2f}")  # Total do item

        y -= 20
        total_nota += total_item

    # Total da nota fiscal
    c.line(50, y - 10, 550, y - 10)  # Linha divisória antes do total
    c.setFont("Helvetica-Bold", 12)
    c.drawString(400, y - 30, "Total:")
    c.drawString(500, y - 30, f"R$ {total_nota:.2f}")

    # Finalizar e salvar o PDF no buffer
    c.showPage()
    c.save()

    # Mover o ponteiro para o início do buffer para leitura
    buffer.seek(0)

    return buffer

def abort_if_cliente_not_exists(cliente_id):
    cliente = Cliente.query.filter_by(id=cliente_id).first()
    if not cliente:
        return abort(400, "Cliente nao existente")
    return cliente

def abort_if_categoria_not_exists(categoria_id):
    categoria = Categoria.query.filter_by(id=categoria_id).first()
    if not categoria:
        return abort(400, "Categoria nao existente")
    return categoria

def abort_if_produto_not_exists(produto_id):
    produto = Produto.query.filter_by(id=produto_id).first()
    if not produto:
        return abort(400, "produto nao existente")
    return produto

def abort_if_fornecedor_not_exists(fornecedor_id):
    fornecedor = Fornecedor.query.filter_by(id=fornecedor_id).first()
    if not fornecedor:
        return abort(400, "Fornecedor nao existente")
    return fornecedor

def abort_if_item_not_exists(item_id):
    item = Item.query.filter_by(id=item_id).first()
    if not item:
        return abort(400, "Item nao existente")
    return item

def att2f(id_usuario):
    with app.app_context():
        query = Usuario.query.filter_by(id=id_usuario).first()
        code = ''.join(random.choices(string.digits, k=7))
        query.twofactorcode = code
        database.session.commit()
        database.session.close()
        #sendEmail(str(code), "motoca032125@gmail.com")
        return code #DEBUG ONLYS

class Login(Resource):
    def post(self):
        # Endereço IP de origem (cliente)
        ip_origem = request.remote_addr
        # Endereço IP de destino (servidor Flask)
        ip_destino = request.host
        #print(ip_origem, ip_destino)
        data = request.json
        usuario = Usuario.query.filter_by(email=data["email"]).first()
        if not usuario or not bcrypt.check_password_hash(usuario.passwd, data["pswd"]):
            return jsonify({ "msg":"Email/Senha Incorreto." }), 401  
        #cod = att2f(usuario.id)
        #response = make_response({"2f_token":f"{cod}"}, 200)
        access_token = create_access_token(identity=usuario.id)
        response = make_response({"token":f"{access_token}"}, 200)
        response.headers["Content-Type"] = "application/json"
        response.headers["token"] = f"{access_token}"
        return response

class Home(Resource):
    def get(self):
        return "IF THE POLICE CANT STOP YOU YOU MUST BE ON THE DUST", 200

class RotaCliente(Resource):
    @jwt_required()
    def get(self):
        try:
            cliente_id = request.args.get("id")
            cliente_nome = request.args.get("nome")
            cliente_email = request.args.get("email")
            cliente_documento = request.args.get("documento")
            cliente_pjpf = request.args.get("pjpf")

            if cliente_id:
                query = Cliente.query.filter_by(id=cliente_id).first()
                if not query:
                    return {"msg":"Cliente nao encontrado"}, 404
                json = Cliente.to_dict(query)
            elif cliente_nome:
                query =  Cliente.nome.ilike(f"%{cliente_nome}%").first()
                if not query:
                    return {"msg":"Cliente nao encontrado"}, 404
                json = Cliente.to_dict(query)
            elif cliente_email:
                query =  Cliente.email.ilike(f"%{cliente_email}%").first()
                if not query:
                    return {"msg":"Cliente nao encontrado"}, 404
                json = Cliente.to_dict(query)
            elif cliente_documento:
                query =  Cliente.documento.ilike(f"%{cliente_documento}%").first()
                if not query:
                    return {"msg":"Cliente nao encontrado"}, 404
                json = Cliente.to_dict(query)
            elif cliente_pjpf:
                query =  Cliente.query.filter_by(pjpf=cliente_pjpf).all()
                if not query:
                    return {"msg":"Cliente nao encontrado"}, 404
                lista = [Cliente.to_dict(item) for item in query]
                json = jsonify(lista)
            else:
                query =  Cliente.query.all()
                if not query:
                    return {"msg":"Sem Clientes no banco"}, 404
                lista = [Cliente.to_dict(item) for item in query]
                json = jsonify(lista)

            response = make_response(json, 200)
            response.headers["Content-Type"] = "aplication/json"
            response.headers["token"] = create_access_token(identity=get_jwt_identity())
            return response
        except:
            return jsonify({"msg":"erro interno"}), 500

    @jwt_required()
    def post(self):
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
    
    @jwt_required()
    def patch(self):
        data = request.json
        cliente_id = request.args.get("id")
        cliente = abort_if_cliente_not_exists(cliente_id=cliente_id)
        if "nome" in data:
            cliente.nome = data["nome"]
        if "email" in data:
            cliente.email = data["email"]  
        if "pjpf" in data:
            cliente.pjpf = data["pjpf"]     
        if "documento" in data:
            cliente.documento = data["documento"]

        database.session.commit()
        
        response = make_response(cliente.to_dict(), 200)
        response.headers["Content-Type"] = "application/json"
        response.headers["token"] = create_access_token(identity=get_jwt_identity())
        return response

    @jwt_required()
    def delete(self):
        cliente_id = request.args.get("id")
        cliente = abort_if_cliente_not_exists(cliente_id=cliente_id)
        database.session.delete(cliente)
        database.session.commit()

        response = make_response({"msg":"sucesso"}, 200)
        response.headers["Content-Type"] = "application/json"
        response.headers["token"] = create_access_token(identity=get_jwt_identity())
        return response

class RotaCategoria(Resource):
    @jwt_required()
    def get(self):
        categoria_id = request.args.get("id")
        categoria_nome = request.args.get("nome")
        
        if categoria_id:
            query = Categoria.query.filter_by(id=categoria_id).first()
            if not query:
                return {"msg":"categoria nao encontrada"}, 400
            json = Categoria.to_dict(query)
        elif categoria_nome:
            query = Categoria.query.filter( Categoria.nome.ilike(f"%{categoria_nome}%") ).first()
            if not query:
                return {"msg":"categoria nao encontrada"}, 400
            json = Categoria.to_dict(query)
        else:
            query = Categoria.query.all()
            if not query:
                return {"msg":"Sem itens no banco"}, 404
            lista = [Categoria.to_dict(item) for item in query]
            json = jsonify(lista)

        response = make_response(json, 200)
        response.headers["Content-Type"] = "application/json"
        response.headers["token"] = create_access_token(identity=get_jwt_identity())
        return response
    
    @jwt_required()
    def post(self):
        data = request.json
        if not "descricao" and "nome" in data:
            return jsonify( {"msg":"Erro de parametros"} ), 422
        query = Categoria.query.filter_by(nome=data["nome"]).first()
        if query:
            return {"msg":"Ja Existente"}, 422
        with app.app_context():
            database.session.add( Categoria(nome=data["nome"],descricao=data["descricao"]) )
            database.session.commit()
            database.session.close()
        response = make_response(jsonify({"msg":"Sucess"}), 200)
        response.headers["Content-Type"] = "application/json"
        response.headers["token"] = create_access_token(identity=get_jwt_identity())
        return response
    
    @jwt_required()
    def patch(self):
        data = request.json
        categoria_id = request.args.get("id")
        categoria = abort_if_categoria_not_exists(categoria_id=categoria_id)
        if "nome" in data:
            categoria.nome = data["nome"]
        if "descricao" in data:
            categoria.descricao = data["descricao"]      

        database.session.commit()
        
        response = make_response(categoria.to_dict(), 200)
        response.headers["Content-Type"] = "application/json"
        response.headers["token"] = create_access_token(identity=get_jwt_identity())
        return response
    
    @jwt_required()
    def delete(self):
        categoria_id = request.args.get("id")
        categoria = abort_if_categoria_not_exists(categoria_id=categoria_id)
        database.session.delete(categoria)
        database.session.commit()

        response = make_response({"msg":"sucesso"}, 200)
        response.headers["Content-Type"] = "application/json"
        response.headers["token"] = create_access_token(identity=get_jwt_identity())
        return response
    
class RotaFornecedor(Resource):
    @jwt_required()
    def get(self):
        fornecedor_id = request.args.get("id")
        fornecedor_nome = request.args.get("nome")
        fornecedor_email = request.args.get("email")
        fornecedor_cnpj = request.args.get("cnpj")

        if fornecedor_id:
            query = Fornecedor.query.filter_by(id=fornecedor_id).first()
            if not query:
                return {"msg":"Fornecedor nao encontrado"}, 400
            json = Fornecedor.to_dict(query)
        elif fornecedor_nome:
            query = Fornecedor.query.filter( Fornecedor.nome.ilike(f"%{fornecedor_nome}%") ).all()
            if not query:
                return {"msg":"Fornecedor nao encontrado"}, 400
            lista = [Cliente.to_dict(item) for item in query]
            json = jsonify(lista)
        elif fornecedor_email:
            query = Fornecedor.query.filter( Fornecedor.email.ilike(f"%{fornecedor_email}%") ).all()
            if not query:
                return {"msg":"Fornecedor nao encontrado"}, 400
            lista = [Cliente.to_dict(item) for item in query]
            json = jsonify(lista)
        elif fornecedor_cnpj:
            query = Fornecedor.query.filter_by(cnpj=fornecedor_cnpj).first()
            if not query:
                return {"msg":"Fornecedor nao encontrado"}, 400
            json = Fornecedor.to_dict(query)
        else:
            query = Fornecedor.query.all()
            if not query:
                return {"msg":"Sem fornecedores no banco"}, 400
            lista = [Fornecedor.to_dict(item) for item in query]
            json = jsonify(lista)

        
        response = make_response(json, 200)
        response.headers["Content-Type"] = "application/json"
        response.headers["token"] = create_access_token(identity=get_jwt_identity())
        return response
    
    @jwt_required()
    def post(self):
        data = request.json

        if not "email" in data or not "nome" in data or not "cnpj" in data:
            return {"msg":"Erro de parametros"}, 422
        if Fornecedor.query.filter_by(nome=data["nome"]).first():
            return {"msg":"Nome Ja Existente"}, 422
        if Fornecedor.query.filter_by(email=data["email"]).first():
            return {"msg":"Email Ja Existente"}, 422
        if Fornecedor.query.filter_by(cnpj=data["cnpj"]).first():
            return {"msg":"cnpj Ja Existente"}, 422
        
        with app.app_context():
            database.session.add( Fornecedor(nome=data["nome"],email=data["email"],cnpj=data["cnpj"]) )
            database.session.commit()
            database.session.close()
        resposta = make_response(jsonify({"msg":"Sucess"}), 200)
        resposta.headers["Content-Type"] = "application/json"
        resposta.headers["token"] = create_access_token(identity=get_jwt_identity())
        return resposta
    
    @jwt_required()
    def patch(self):
        data = request.json
        fornecedor_id = request.args.get("id")
        fornecedor = abort_if_fornecedor_not_exists(fornecedor_id=fornecedor_id)
        if "nome" in data:
            if Fornecedor.query.filter_by(nome=data["nome"]).first():
                return {"msg":"Nome ja registrado"}, 400
            fornecedor.nome = data["nome"]
        if "cnpj" in data:
            if Fornecedor.query.filter_by(cnpj=data["cnpj"]).first():
                return {"msg":"cnpj ja registrado"}, 400
            fornecedor.cnpj = data["cnpj"]      ##### 
        if "email" in data:
            if Fornecedor.query.filter_by(email=data["email"]).first():
                return {"msg":"Email ja registrado"}, 400
            fornecedor.email = data["email"]

        database.session.commit()
        
        response = make_response(Fornecedor.to_dict(fornecedor), 200)
        response.headers["Content-Type"] = "application/json"
        response.headers["token"] = create_access_token(identity=get_jwt_identity())
        return response
    
    @jwt_required()
    def delete(self):
        fornecedor_id = request.args.get("id")
        fornecedor = abort_if_fornecedor_not_exists(fornecedor_id=fornecedor_id)
        database.session.delete(fornecedor)
        database.session.commit()

        response = make_response({"msg":"sucesso"}, 200)
        response.headers["Content-Type"] = "application/json"
        response.headers["token"] = create_access_token(identity=get_jwt_identity())
        return response

class RotaProduto(Resource):
    @jwt_required()
    def get(self):
        try:
            produto_id = request.args.get("id")
            produto_nome = request.args.get("nome")
            produto_descricao = request.args.get("descricao")
            produto_id_fornecedor = request.args.get("id_fornecedor")
            produto_id_categoria = request.args.get("id_categoria")
            
            if produto_id:
                query = Produto.query.filter_by(id=produto_id).first()
                if not query:
                    return {"msg":"Nenhum produto encontrado"}, 404
                json = Produto.to_dict(query)
            elif produto_nome:
                query = Produto.query.filter( Produto.nome.ilike(f"%{produto_nome}%") ).all()
                if not query:
                    return {"msg":"Nenhum produto encontrado"}, 404
                lista = [Produto.to_dict(item) for item in query]
                json = jsonify(lista)
            elif produto_descricao:
                query = Produto.query.filter( Produto.descricao.ilike(f"%{produto_descricao}%") ).all()
                if not query:
                    return {"msg":"Nenhum produto encontrado"}, 404
                lista = [Produto.to_dict(item) for item in query]
                json = jsonify(lista)
            elif produto_id_fornecedor:
                query = Produto.query.filter_by(id_fornecedor=produto_id_fornecedor).all()
                if not query:
                    return {"msg":"Nenhum produto encontrado"}, 404
                lista = [Produto.to_dict(item) for item in query]
                json = jsonify(lista)
            elif produto_id_categoria:
                query = Produto.query.filter_by(id_categoria=produto_id_categoria).all()
                if not query:
                    return {"msg":"Nenhum produto encontrado"}, 404
                lista = [Produto.to_dict(item) for item in query]
                json = jsonify(lista)
            else:
                query = Produto.query.all()
                if not query:
                    return {"msg":"Sem produtos no banco"}, 404
                lista = [Produto.to_dict(item) for item in query]
                json = jsonify(lista)

            response = make_response(json, 200)
            response.headers["Content-Type"] = "application/json"
            response.headers["token"] = create_access_token(identity=get_jwt_identity())
            return response
        except:
            return jsonify({"msg":"erro interno"}), 500
    
    @jwt_required()
    def post(self): 
        data = request.json
        query = Produto.query.filter_by(nome=data["nome"]).first()
        if query:
            return jsonify( {"msg":"Um produto ja foi cadastrado com esse nome"} ) , 409
        try:
            with app.app_context():
                database.session.add( Produto(nome=data["nome"], descricao=data["descricao"], id_fornecedor=data["id_fornecedor"], id_categoria=data["id_categoria"]) )
                database.session.commit()
                database.session.close()
            resposta = make_response(jsonify({"msg":"Sucess"}), 200)
            resposta.headers["Content-Type"] = "application/json"
            resposta.headers["token"] = create_access_token(identity=get_jwt_identity())
            return resposta
        except:
            return jsonify( {"msg":"Failure"} ) , 500
        
    @jwt_required()
    def patch(self):
        data = request.json
        produto_id = request.args.get("id")
        produto = abort_if_produto_not_exists(produto_id=produto_id)
        if "nome" in data:
            produto.nome = data["nome"]
        if "descricao" in data:
            produto.descricao = data["descricao"]    
        if "id_fornecedor" in data:
            produto.id_fornecedor = data["id_fornecedor"]
        if "id_categoria" in data:
            produto.id_categoria = data["id_categoria"]
        if "deletado" in data:
            if data["deletado"] == "True":
                produto.deletado = True
            else:
                produto.deletado == False
            produto.deletado = data["deletado"]

        database.session.commit()
        
        response = make_response(Produto.to_dict(produto), 200)
        response.headers["Content-Type"] = "application/json"
        response.headers["token"] = create_access_token(identity=get_jwt_identity())
        return response
    
    @jwt_required()
    def delete(self):
        produto_id = request.args.get("id")
        produto = abort_if_produto_not_exists(produto_id=produto_id)
        database.session.delete(produto)
        database.session.commit()

        response = make_response({"msg":"sucesso"}, 200)
        response.headers["Content-Type"] = "application/json"
        response.headers["token"] = create_access_token(identity=get_jwt_identity())
        return response
        
class RotaItem(Resource):
    @jwt_required()
    def get(self):
        item_id = request.args.get("id")
        item_id_produto = request.args.get("id_produto")
        item_status = request.args.get("id_status")
        item_id_entrada = request.args.get("id_entrada")
        item_id_saida = request.args.get("id_saida")

        if item_id:
            query = Item.query.filter_by(id=item_id).first()
            if not query:
                return {"msg":"Nenhum item encontrado"}, 400
            json = Item.to_dict(query)
        elif item_id_produto:
            query = Item.query.filter_by(id_produto=item_id_produto).all()
            if not query:
                return {"msg":"Nenhum item encontrado"}, 400
            lista = [Item.to_dict(item) for item in query]
            json = jsonify(lista)
        elif item_status:
            query = Item.query.filter_by(status=item_status).all()
            if not query:
                return {"msg":"Nenhum item encontrado"}, 400
            lista = [Item.to_dict(item) for item in query]
            json = jsonify(lista)
        elif item_id_entrada:
            query = Item.query.filter_by(id_entrada=item_id_entrada).first()
            if not query:
                return {"msg":"Nenhum item encontrado"}, 400
            json = Item.to_dict(query)
        elif item_id_saida:
            query = Item.query.filter_by(id_saida=item_id_saida).first()
            if not query:
                return {"msg":"Nenhum item encontrado"}, 400
            json = Item.to_dict(query)
        else:
            query = Item.query.all()
            if not query:
                return {"msg":"Sem itens no banco"}, 400
            lista = [Item.to_dict(item) for item in query]
            json = jsonify(lista)

        
        resposta = make_response(json, 200)
        resposta.headers["Content-Type"] = "application/json"
        resposta.headers["token"] = create_access_token(identity=get_jwt_identity())
        return resposta
    
    @jwt_required()
    def post(self):
        data = request.json
        usuario_atual = get_jwt_identity()
        nova_entrada = Entrada(id_usuario=usuario_atual, data=datetime.now())
        database.session.add(nova_entrada)
        database.session.commit()

        for item in data:
            query_produto = Produto.query.filter_by(id=item["id_produto"]).first()
            if not query_produto:
                return {"msg":"ID Produto nao encontrado"}, 400
            query_produto.quantidade = int( query_produto.quantidade ) + 1
            novo_item = Item(id_produto=item["id_produto"], valor_compra=item["valor_compra"], id_entrada=nova_entrada.id)
            database.session.add(novo_item)
            database.session.commit()

        database.session.close()

        resposta = make_response({"msg":"Sucesso"}, 200)
        resposta.headers["Content-Type"] = "application/json"
        resposta.headers["token"] = create_access_token(identity=get_jwt_identity())
        return resposta
    
    @jwt_required()
    def patch(self):
        data = request.json
        item_id = request.args.get("id")
        item = abort_if_item_not_exists(item_id=item_id)
        
        if "status" in data:
            if data["status"] == "VENDIDO":
                item.status = "VENDIDO"
            else:
                item.status = "ESTOQUE"
        if "valor_venda" in data:
            item.valor_venda = data["valor_venda"]
        if "valor_compra" in data:
            item.valor_compra = data["valor_compra"]
        if "id_produto" in data:
            item.id_produto = data["id_produto"]
        if "id_entrada" in data:
            item.id_entrada = data["id_entrada"]
        if "id_saida" in data:
            item.id_saida = data["id_saida"]

        database.session.commit()
        
        response = make_response(Item.to_dict(item), 200)
        response.headers["Content-Type"] = "application/json"
        response.headers["token"] = create_access_token(identity=get_jwt_identity())
        return response
    
    @jwt_required()
    def delete(self):
        item_id = request.args.get("id")
        item = abort_if_item_not_exists(item_id=item_id)
        database.session.delete(item)
        database.session.commit()

        response = make_response({"msg":"sucesso"}, 200)
        response.headers["Content-Type"] = "application/json"
        response.headers["token"] = create_access_token(identity=get_jwt_identity())
        return response
        
class RotaSaida(Resource):
    @jwt_required()
    def get(self):
        saida_id = request.args.get("id")
        saida_id_usuario= request.args.get("id_usuario")
        saida_id_cliente= request.args.get("id_cliente")
        if saida_id:
            query = Saida.query.filter_by(id=data["id"]).first()
            if not query:
                return {"msg":"Saida nao encontrada"} , 400
            json = Saida.to_dict(query)
        elif saida_id_usuario:
            query = Saida.query.filter_by(id_usuario=saida_id_usuario).all()
            if not query:
                return {"msg":"Saida nao encontrada"} , 400
            lista = [Saida.to_dict(item) for item in query]
            json = jsonify(lista)
        elif saida_id_cliente:
            query = Saida.query.filter_by(id_cliente=saida_id_cliente).all()
            if not query:
                return {"msg":"Saida nao encontrada"} , 400
            lista = [Saida.to_dict(item) for item in query]
            json = jsonify(lista)
        else:
            query = Saida.query.all()
            if not query:
                return {"msg":"Sem saidas no banco"} , 400
            lista = [Saida.to_dict(item) for item in query]
            json = jsonify(lista)

        resposta = make_response(json, 200)
        resposta.headers["Content-Type"] = "application/json"
        resposta.headers["token"] = create_access_token(identity=get_jwt_identity())
        return resposta

    @jwt_required()
    def post(self):
        data = request.json
        usuario_atual = get_jwt_identity()

        # CHECA SE OS PARAMETROS ESTAO NA REQUISICAO
        if not "id_cliente" in data and not "itens" in data:
            return {"msg":"Erro de parametros"}, 422
        
        # Consulta do cliente
        queryCliente = Cliente.query.filter_by(id=data["id_cliente"]).first()
        if not queryCliente:
            return {"msg": "Cliente nao encontrado"}, 422
        
        # CHECA SE OS ITENS EXISTEM E ESTAO EM ESTOQUE
        itens = data.get('itens')
        for i in itens:
            if not "id" in i or not "valor_venda" in i:
                return {"msg":"Erro de parametros de item"}, 422
            query = Item.query.filter_by(id=i["id"]).first()
            if not query or query.status == "VENDIDO":
                return {"msg":f"O item de id {i['id']} nao foi encontrado ou nao esta mais em estoque"}, 422

        # Criar nova Saída
        nova_saida = Saida(id_usuario=usuario_atual, id_cliente=queryCliente.id, data=datetime.now())
        database.session.add(nova_saida)
        database.session.commit()
        itens_vendidos = []
        
        # Processar os itens
        for i in data["itens"]:
            query = Item.query.filter_by(id=i["id"]).first()
            if query:
                query.status = "VENDIDO"
                query.valor_venda = i["valor_venda"]
                query.id_saida = nova_saida.id
                itens_vendidos.append(query.id)
        
        database.session.commit()

        # Gerar o PDF da nota fiscal
        pdf_buffer = gerar_nota_fiscal_pdf(nova_saida.id, queryCliente, itens_vendidos)

        # Gerar um novo token JWT
        novo_token = create_access_token(identity=usuario_atual)

        # Retornar o PDF com o novo token no corpo da resposta
        resposta = make_response(send_file(pdf_buffer, as_attachment=True, download_name=f'nota_fiscal_{nova_saida.id}.pdf', mimetype='application/pdf'))
        resposta.headers["token"] = novo_token
        return resposta

class RotaEntrada(Resource):
    @jwt_required() 
    def get(self):
        entrada_id = request.args.get("id")
        entrada_id_usuario= request.args.get("id_usuario")
        if entrada_id:
            query = Entrada.query.filter_by(id=entrada_id).first()
            if not query:
                return {"msg":"Entrada nao encontrada"} , 400
            json = Entrada.to_dict(query)
        elif entrada_id_usuario:
            query = Entrada.query.filter_by(id_usuario=entrada_id_usuario).all()
            if not query:
                return {"msg":"Entrada nao encontrada"} , 400
            lista = [Entrada.to_dict(item) for item in query]
            json = jsonify(lista)
        else:
            query = Entrada.query.all()
            if not query:
                return {"msg":"Sem entradas no banco"} , 400
            lista = [Entrada.to_dict(item) for item in query]
            json = jsonify(lista)

        resposta = make_response(json, 200)
        resposta.headers["Content-Type"] = "application/json"
        resposta.headers["token"] = create_access_token(identity=get_jwt_identity())
        return resposta
    
api.add_resource(Home,"/api/")
api.add_resource(Login,"/api/login")
api.add_resource(RotaCliente,"/api/Cliente")
api.add_resource(RotaCategoria,"/api/Categoria")
api.add_resource(RotaFornecedor,"/api/Fornecedor")
api.add_resource(RotaProduto,"/api/Produto")
api.add_resource(RotaItem,"/api/Item")
api.add_resource(RotaSaida,"/api/Saida")
api.add_resource(RotaEntrada,"/api/Entrada")

######################################################################################################

# @jwt.user_lookup_loader
# def user_lookup_callback(_jwt_header, jwt_data):
#     identity = jwt_data["id"]
#     return database.session.get(Usuario, identity) #Usuario.query.get(identity)

######################################################################################################
