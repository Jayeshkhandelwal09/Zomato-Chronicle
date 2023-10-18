import json
import pytest
from ..app import app, menu, save_menu_to_json

@pytest.fixture
def client():
    app.config['TESTING'] = True
    client = app.test_client()
    yield client

def test_add_dish(client):
    # Clear the menu before testing
    menu.clear()
    save_menu_to_json(menu)

    # Send a POST request with form data
    response = client.post('/add_dish', data={
        'dish_id': '1',
        'dish_name': 'Test Dish',
        'dish_price': '10.99',
        'available': 'on'  # Simulate checkbox being checked
    })

    # Check if the response redirects to the menu page
    assert response.status_code == 302
    assert response.headers['Location'] == 'http://localhost/menu'

    # Check if the dish was added to the menu
    assert len(menu) == 1
    assert menu[0]['id'] == '1'
    assert menu[0]['name'] == 'Test Dish'
    assert menu[0]['price'] == 10.99
    assert menu[0]['available'] is True
