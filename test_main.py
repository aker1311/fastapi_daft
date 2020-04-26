from fastapi.testclient import TestClient

from main import app

import pytest

client = TestClient(app)

def test_hello_word():
    response = client.get('/')
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World during the coronavirus pandemic!"}

@pytest.mark.parametrize("name", ["Zenek", "Marek", "Alojzy Niezdąży"])
def test_hello_name(name):
    response = client.get(f'/hello/{name}')
    assert response.status_code == 200
    assert response.json() == {"msg":  f"Hello {name}"}

def test_get_patient():
    for i in range(1,3):
        response = client.post('/patient', json={'name': 'Jan', 'surname': 'Kowalski'})
        assert response.status_code == 200
        assert response.json() == {'id': i, 'patient': {'name': 'Jan', 'surname': 'Kowalski'}}
