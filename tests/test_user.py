from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)

# Существующие пользователи (из fake_db)
users = [
    {
        'id': 1,
        'name': 'Ivan Ivanov',
        'email': 'i.i.ivanov@mail.com',
    },
    {
        'id': 2,
        'name': 'Petr Petrov',
        'email': 'p.p.petrov@mail.com',
    }
]

def test_get_existed_user():
    '''Получение существующего пользователя'''
    response = client.get("/api/v1/user", params={'email': users[0]['email']})
    assert response.status_code == 200
    assert response.json()['id'] == users[0]['id']
    assert response.json()['name'] == users[0]['name']
    assert response.json()['email'] == users[0]['email']

def test_get_unexisted_user():
    '''Получение несуществующего пользователя'''
    response = client.get("/api/v1/user", params={'email': 'nonexistent@mail.com'})
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}

def test_create_user_with_valid_email():
    '''Создание пользователя с уникальной почтой'''
    new_user = {
        'name': 'Test User',
        'email': 'test@mail.com'
    }
    response = client.post("/api/v1/user", json=new_user)
    assert response.status_code == 201  # Created
    user_id = response.json()  # возвращает id (int)
    assert isinstance(user_id, int)
    
    # Проверим, что пользователь действительно создался
    get_response = client.get("/api/v1/user", params={'email': 'test@mail.com'})
    assert get_response.status_code == 200
    assert get_response.json()['name'] == 'Test User'

def test_create_user_with_invalid_email():
    '''Создание пользователя с почтой, которую использует другой пользователь'''
    existing_user = {
        'name': 'Duplicate Name',
        'email': users[0]['email']  # email первого существующего пользователя
    }
    response = client.post("/api/v1/user", json=existing_user)
    assert response.status_code == 409  # Conflict
    assert response.json() == {"detail": "User with this email already exists"}

def test_delete_user():
    '''Удаление пользователя'''
    # Сначала создадим пользователя для удаления
    new_user = {
        'name': 'To Delete',
        'email': 'todelete@mail.com'
    }
    create_response = client.post("/api/v1/user", json=new_user)
    assert create_response.status_code == 201
    user_id = create_response.json()
    
    # Теперь удалим его по email
    delete_response = client.delete("/api/v1/user", params={'email': 'todelete@mail.com'})
    assert delete_response.status_code == 204  # No Content
    assert delete_response.text == ""  # Пустой ответ
    
    # Проверим, что пользователь действительно удалён
    get_response = client.get("/api/v1/user", params={'email': 'todelete@mail.com'})
    assert get_response.status_code == 404
    assert get_response.json() == {"detail": "User not found"}