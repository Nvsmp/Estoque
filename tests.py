import pytest
from projeto import app

@pytest.fixture(scope='module')
def session():
    return {}

def attSession(token,session):
    session["jwt_token"] = token#rsp.headers["token"]
    session["auth"] = {
        "Authorization":f"Bearer { str(session["jwt_token"]) }"
    }

@pytest.fixture(scope="module")
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_non_existent_page(client):
    """Testa uma página inexistente"""
    rsp = client.get('/non-existent')
    assert rsp.status_code == 404

##### LOGIN #####
def test_login(client, session):
    """Testa a página principal"""
    rsp = client.get('/api/login',json={"email":"teste","pswd":"123"})
    session["2f"] = rsp.json["2f_token"]
    assert rsp.status_code == 200

##### 2Fcod #####
def test_2fc(client, session):
    rsp = client.get("/api/2f", json={"email":"teste","2fc":session["2f"]})
    assert rsp.status_code == 200
    attSession(rsp.json.get("token"), session)
    assert session["jwt_token"] is not None
    
##### HOME #####
def test_home(client, session):
    rsp = client.get("/",headers=session["auth"])
    assert rsp.status_code == 200

##### ADD FORNECEDOR #####  
def test_fornecedor(client, session):
    json = {"nome":"Phillies", "email":"emailPhilies@teste.com", "cnpj":"XX.XXX.XXX/0001-AA"}
    rsp = client.post("/api/Fornecedor", headers=session["auth"], json=json)
    assert rsp.status_code == 200
    attSession(rsp.headers["token"], session)

##### ADD CATEGORIA #####
def test_categoria(client, session):
    json = {"nome":"Tabacaria", "descricao":"Produtos e insumos para tabacaria"}
    rsp = client.post("/api/Categoria", headers=session["auth"], json=json)
    assert rsp.status_code == 200
    attSession(rsp.headers["token"], session)

##### ADD CLIENTE #####
def test_cliente(client, session):
    json = {"nome":"Joaozinho", "email":"cliente@teste.com", "pjpf":"F", "documento":"123.456.789-10"}
    rsp = client.post("/api/Cliente", headers=session["auth"], json=json)
    assert rsp.status_code == 200
    attSession(rsp.headers["token"], session)

##### ADD PRODUTO #####
def test_addProduto(client, session):
    json = {
        "nome":"Charuto Titan Chocolate",
        "descricao":"Charuto com sabor de chocolate",
        "id_fornecedor":"1",
        "id_categoria":"1"
        }
    rsp = client.post("/api/Produto",headers=session["auth"], json=json)
    assert rsp.status_code == 200
    attSession(rsp.headers["token"], session)

##### PATCH PRODUTO #####
# def test_patchProduto(client,session):
#     rsp1 = client.patch("/api/patchProduto",headers=session["auth"],json={"id":"1","new_nome":"Charuto Titan Conhaque"})
#     assert rsp1.status_code == 409
#     rsp2 = client.patch("/api/patchProduto",headers=session["auth"],json={"id":"2","new_nome":"Charuto Titan Chocolate"})
#     assert rsp2.status_code == 409
#     rsp3 = client.patch("/api/patchProduto",headers=session["auth"],json={"id":"1","new_nome":"Charuto Titan Chocolate"})
#     assert rsp3.status_code == 200
#     attSession(rsp3.headers["token"], session)

##### ADD ITEM #####
def test_addItem(client, session):
    json = { "itens": [
        { "id_produto":"1", "valor_compra":"19.99" },
        { "id_produto":"1", "valor_compra":"19.99" },
        { "id_produto":"1", "valor_compra":"19.99" }] 
    }
    rsp = client.post("/api/Item",headers=session["auth"],json=json)
    assert rsp.status_code == 200
    attSession(rsp.headers["token"], session)
    # rsp2 = client.post("/api/addItem",headers=session["auth"],json={"id_produto":"2","valor_compra":"19.99" })
    # assert rsp2.status_code == 404
    # rsp3 = client.post("/api/addItem",headers=session["auth"],json={"id_produto":"1","valor_compra":"18.99" })
    # assert rsp3.status_code == 200
    # attSession(rsp3.headers["token"], session)  

##### ADD SAIDA #####
def test_saida(client, session):
    json = {   
        "id_cliente":"1", "valor_compra":"19.99",
        "itens": ["1","2"]
    }
    rsp = client.post("/api/Saida",headers=session["auth"],json=json)
    assert rsp.status_code == 200
    attSession(rsp.headers["token"], session)

##### DELETE PRODUTO #####
# def test_deleteProduto(client,session):
#     rsp = client.delete("/api/deleteProduto",headers=session["auth"],json={"id":"1"})
#     assert rsp.status_code == 200
#     attSession(rsp.headers["token"], session)
#     rsp2 = client.delete("/api/deleteProduto",headers=session["auth"],json={"id":"1"})
#     assert rsp2.status_code == 409



    

