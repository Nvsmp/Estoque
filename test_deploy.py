import pytest, requests, os

link = "http://127.0.0.1:5000/api/"

@pytest.fixture(scope='module')
def session():
    return {}

def attSession(token, session):
    session["jwt_token"] = token
    session["auth"] = {
        "Authorization": f"Bearer {str(session['jwt_token'])}"
    }

def test_404():
    resp = requests.get(link + "wabalabadubdub")
    assert resp.status_code == 404

def test_home():
    resp = requests.get(link)
    print(resp.text)
    assert resp.status_code == 200

def test_login(session):
    json = {"email": "ademir@teste.com", "pswd": "senha123"}
    resp = requests.post(url=link + "login", json=json)
    assert resp.status_code == 200
    token = resp.headers["token"]
    attSession(token, session)

def test_postCliente(session):
    json = {
        "nome": "duelverson",
        "email": "duelverson@totomail.com",
        "pjpf": "F",
        "documento": "000.000.000.00",
    }
    resp = requests.post(url=link + "Cliente", json=json, headers=session["auth"])
    assert resp.status_code == 200
    attSession(resp.headers["token"], session)

def test_postFornecedor(session):
    json = {
        "nome": "astrazeneca",
        "email": "astrazeneca@gmail.com",
        "cnpj": "123.567.911.345.78"
    }
    resp = requests.post(url=link + "Fornecedor", json=json, headers=session["auth"])
    assert resp.status_code == 200
    attSession(resp.headers["token"], session)

########################################### PATCH E DELETE

def test_postCategoria(session):
    json = {
        "nome": "sucos",
        "descricao": "ajudinha ne rs",
    }
    resp = requests.post(url=link + "Categoria", json=json, headers=session["auth"])
    assert resp.status_code == 200
    attSession(resp.headers["token"], session)

def test_postProduto(session):
    json = {
        "nome": "trembolona",
        "descricao": "enantado de testosterona",
        "id_fornecedor": "1",
        "id_categoria": "1"
    }
    resp = requests.post(url=link + "Produto", json=json, headers=session["auth"])
    assert resp.status_code == 200
    attSession(resp.headers["token"], session)

def test_postItem(session):
    json = [{"id_produto": "1", "valor_compra": "36.90"},
            {"id_produto": "1", "valor_compra": "37.00"},
            {"id_produto": "1", "valor_compra": "36.80"}] 
    resp = requests.post(url=link + "Item", json=json, headers=session["auth"])
    assert resp.status_code == 200
    attSession(resp.headers["token"], session)

def test_getCliente(session):
    resp = requests.get(url=link + "Cliente?id=1", headers=session["auth"])
    assert resp.status_code == 200
    attSession(resp.headers["token"], session)

def test_patchCliente(session):
    json = {
        "nome": "duelverson",
        "email": "duelverson@totomail.com",
        "pjpf": "J",
        "documento": "010.010.010.10"
    }
    resp = requests.patch(url=link + "Cliente?id=1", headers=session["auth"], json=json)
    assert resp.status_code == 200
    attSession(resp.headers["token"], session)

########################################### Teste de geração de PDF

def test_postSaidaGeraPDF(session):
    # Dados para a criação da saída
    json = {
        "id_cliente": 1,  # Id de um cliente válido
        "itens": [{"id":1,"valor_venda":19.99}]  # Lista de itens válidos
    }
    
    # Enviar requisição POST para a rota de Saída
    resp = requests.post(url=link + "Saida", json=json, headers=session["auth"])
    
    # Verifica se a resposta é bem-sucedida (status 200)
    assert resp.status_code == 200

    # Verifica se o conteúdo retornado é um PDF
    assert resp.headers["Content-Type"] == "application/pdf"

    # Salvar o PDF na pasta do teste
    file_path = os.path.join(os.path.dirname(__file__), "nota_fiscal_test.pdf")
    with open(file_path, "wb") as f:
        f.write(resp.content)

    print(f"PDF gerado e salvo em: {file_path}")
    attSession(resp.headers["token"], session)

def test_deleteCliente(session):
    resp = requests.delete(url=link + "Cliente?id=1", headers=session["auth"])
    assert resp.status_code == 200
    attSession(resp.headers["token"], session)
