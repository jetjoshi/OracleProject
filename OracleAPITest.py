from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_drop_all_tuples():
    # Test case for drop_all_tuples
    response = client.delete("/drop_all_tuples")
    print(response.content)
    assert response.status_code == 200
    assert "message" in response.json()

def test_create_warehouse_api():
    # Test cases for create_warehouse_api
    payload = {
        "name": "test_warehouse",
        "locationName": "test_location",
        "currentInventory": 10,
        "maxInventory": 20
    }

    # Successful creation
    response = client.post("/warehouse/", json=payload)
    print(response.content)
    assert response.status_code == 200

    # Duplicate warehouse creation
    response = client.post("/warehouse/", json=payload)
    print(response.content)
    assert response.status_code == 402

    # Incorrect payload format
    response = client.post("/warehouse/", json={})
    print(response.content)
    assert response.status_code == 422

def test_create_restaurant_api():
    # Test cases for create_restaurant_api
    payload = {
        "name": "test_restaurant",
        "locationName": "test_location",
        "currentInventory": 10,
        "maxInventory": 20
    }

    payload2 = {
        "name": "restaurant1",
        "locationName": "test_location",
        "currentInventory": 10,
        "maxInventory": 20
    }

    # Successful creation
    response = client.post("/restaurant/", json=payload)
    print(response.content)
    assert response.status_code == 200

    # Successful creation
    response = client.post("/restaurant/", json=payload2)
    print(response.content)
    assert response.status_code == 200

    # Duplicate restaurant creation
    response = client.post("/restaurant/", json=payload)
    print(response.content)
    assert response.status_code == 402

    # Incorrect payload format
    response = client.post("/restaurant/", json={})
    print(response.content)
    assert response.status_code == 422

def test_search_restaurants_api():
    # Test cases for search_restaurants_api
    response = client.post("/restaurant/search", json={"query": "restaurant1"})
    print(response.content)
    assert response.status_code == 200
    assert len(response.json()) > 0

    response = client.post("/restaurant/search", json={"query": ""})
    print(response.content)
    assert response.status_code == 200
    assert len(response.json()) > 0

    # Test case for incorrect payload format
    response = client.post("/restaurant/search", json={})
    print(response.content)
    assert response.status_code == 422


def test_get_restaurant_inventory():
    # Test cases for get_restaurant_inventory
    response = client.get("/restaurant/inventory/restaurant1")
    print(response.content)
    assert response.status_code == 200
    assert "name" in response.json()

    # Test case for non-existing restaurant
    response = client.get("/restaurant/inventory/non_existing_restaurant")
    print(response.content)
    assert response.status_code == 404



def test_decrease_inventory():
    # Test cases for decrease_inventory
    payload = {
        "inventory": 5
    }

    # Successful decrease
    response = client.put("/restaurant/inventory/test_restaurant", json=payload)
    print(response.content)
    assert response.status_code == 200
    assert "message" in response.json()

    # Incorrect payload format
    response = client.put("/restaurant/inventory/test_restaurant", json={})
    print(response.content)
    assert response.status_code == 422


def test_get_all_warehouses():
    # Test case for get_all_warehouses
    response = client.get("/warehouse")
    print(response.content)
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_increase_warehouse_inventory():
    # Test cases for increase_warehouse_inventory
    payload = {
        "inventory": 5
    }

    # Successful increase
    response = client.put("/warehouse/inventory/test_warehouse", json=payload)
    print(response.content)
    assert response.status_code == 200
    assert "message" in response.json()

    # Incorrect payload format
    response = client.put("/warehouse/inventory/test_warehouse", json={})
    print(response.content)
    assert response.status_code == 422


def test_transfer_inventory():
    # Test cases for transfer_inventory
    payload = {
        "inventory": 5
    }

    # Successful transfer
    response = client.post("/transfer/test_warehouse/test_restaurant", json=payload)
    print(response.content)
    assert response.status_code == 200
    assert "message" in response.json()

    # Incorrect payload format
    response = client.post("/transfer/test_warehouse/test_restaurant", json={})
    print(response.content)
    assert response.status_code == 422





if __name__ == "__main__":
    import pytest
    pytest.main()
