from projeto import database, app, bcrypt, request, jsonify
from projeto.models import Usuario, Produto, Item


r = input("[0] SAIR \n[1] RE-CRIAR BD \n[2] EXIBIR PRODUTOS \n[3] EXIBIR ITENS\n[4] ADICIONAR PRODUTO\n[5] ADICIONAR ITEM\n[6] ADICIONAR USUARIO \n[7] EXIBIR USUARIOS\n=: ")


while r != '0':
        if r == '1':
            with app.app_context():
                database.create_all()
                senha_c = bcrypt.generate_password_hash("123")
                database.session.add( Usuario(username="nome", email="teste", grupo="GERENTE", passwd=senha_c) )
                database.session.commit()
                database.session.close()
            
        elif r == '2':
            with app.app_context():
                query = Produto.query.all()
                if query:
                    for p in query:
                        print(f"ID: {p.id} NOME: {p.nome} QUANTIDADE : {p.quantidade}")
        elif r == '3':
            with app.app_context():
                query = Item.query.all()
                if query:
                    for p in query:
                        print(f"ID: {p.id} NOME: { Produto.query.filter_by(id=p.id_produto).first().nome } STATUS : {p.status} valor_compra : {p.valor_compra} valor_venda : {p.valor_venda} id_grupo : {p.id_produto}")
        elif r == '4':
            with app.app_context():
                nome_produto = input("NOME : ")
                database.session.add( Produto(nome=nome_produto) )
                database.session.commit()
                database.session.close()
                
        elif r == '5':
            with app.app_context():
                id_produto = int( input("ID PRODUTO: ") )
                query_produto = Produto.query.filter_by(id=id_produto).first()
                if query_produto:
                    valor_compra = float( input("VALOR COMPRA(0.00): ") )
                    nova_quantidade = int( query_produto.quantidade ) + 1
                    query_produto.quantidade = nova_quantidade
                    database.session.add( Item(valor_compra=valor_compra, id_produto=id_produto) )
                    database.session.commit()
                    database.session.close()
                
        elif r == "6":
            with app.app_context():
                nome_usuario = input("NOME : ")
                grupo = input("GERENTE | FUNCIONARIO : ").upper()
                senha = input("SENHA : ")
                email = input("email : ")
                if not Usuario.query.filter_by(username=nome_usuario).first() and not Usuario.query.filter_by(email=email).first():
                    senha_c = bcrypt.generate_password_hash(senha)
                    if grupo == "GERENTE":
                        database.session.add( Usuario(username=nome_usuario, email=email, grupo="GERENTE", passwd=senha_c) )
                    else:
                        database.session.add( Usuario(username=nome_usuario, email=email, grupo="FUNCIONARIO", passwd=senha_c) )
                    database.session.commit()
                    database.session.close()
                else:
                    print("Usuario ou email ja cadastrados")
        elif r == "7":
            with app.app_context():
                query = Usuario.query.all()
                if query:
                    for u in query:
                        print(f"USERNAME : {u.username} GRUPO : {u.grupo} EMAIL : {u.email} SENHA : {u.passwd} 2F : {u.twofactorcode}")

        r = input("\n=========================================\n\n[0] SAIR \n[1] RE-CRIAR BD \n[2] EXIBIR PRODUTOS \n[3] EXIBIR ITENS\n[4] ADICIONAR PRODUTO\n[5] ADICIONAR ITEM\n[6] ADICIONAR USUARIO \n[7] EXIBIR USUARIOS\n=: ")    