import pytest
from bson import ObjectId
from fastapi.testclient import TestClient

from app import app


@pytest.fixture
def client():
    return TestClient(app)


# Test for the /aiscore endpoint
def test_aiscore_endpoint(client):
    
    # Generate a valid ObjectId as a string
    valid_object_id = str(ObjectId("65840683e93f5452b7b37b66"))

    payload = {"carid": valid_object_id}
    api_key = "lkjINRhG1rKRNc2kE5xfcK0hFJaz6Kvz1jux"

    # Test case for valid input
    response = client.post(f"/aiscore?api_key={api_key}", json=payload)
    assert response.status_code == 200
    assert "Response" in response.json()

    # Test case for invalid car_id
    
    response = client.post(f"/aiscore?api_key={api_key}", json={"carid": "65840683e93f5452b7b37b60"})
    assert response.status_code == 200
    assert "Response" in response.json()
    

    #  # Test case for invalid Object car_id
    # response = client.post("/aiscore", json={"car_data": {"carid": "65840683e93f5452b7b37b"}, "api_key": "lkjINRhG1rKRNc2kE5xfcK0hFJaz6Kvz1jux"})
    # assert response.status_code == 400
    # assert "Invalid car_id" in response.text

    # # Test case for missing api_key
    # response = client.post("/aiscore", json={"car_data": {"carid": "65840683e93f5452b7b37b99"}})
    # assert response.status_code == 422  # HTTP 422 Unprocessable Entity
    # assert "api_key" in response.text

    # # Test case for missing car_id
    # response = client.post("/aiscore", json={"api_key": "lkjINRhG1rKRNc2kE5xfcK0hFJaz6Kvz1jux"})
    # assert response.status_code == 422
    # assert "carid" in response.text

    # # Test case for empty car_id
    # response = client.post("/aiscore", json={"car_data": {"carid": ""}, "api_key": "lkjINRhG1rKRNc2kE5xfcK0hFJaz6Kvz1jux"})
    # assert response.status_code == 422
    # assert "car_id" in response.text


# # Test for the /feedmanager endpoint
# def test_feedmanager_endpoint(client):
#     # Test case for valid input
#     response = client.post("/feedmanager", json={"feed_data": {"user_id": "valid_object_id", "longitude": 0.0, "latitude": 0.0}, "api_key": "valid_api_key"})
#     assert response.status_code == 200
#     assert "output" in response.json()

#     # Test case for invalid user_id
#     response = client.post("/feedmanager", json={"feed_data": {"user_id": "invalid_object_id", "longitude": 0.0, "latitude": 0.0}, "api_key": "valid_api_key"})
#     assert response.status_code == 400
#     assert "Invalid user_id" in response.text

#     # Test case for missing api_key
#     response = client.post("/feedmanager", json={"feed_data": {"user_id": "valid_object_id", "longitude": 0.0, "latitude": 0.0}})
#     assert response.status_code == 422
#     assert "api_key" in response.text

#     # Test case for missing user_id
#     response = client.post("/feedmanager", json={"feed_data": {"longitude": 0.0, "latitude": 0.0}, "api_key": "valid_api_key"})
#     assert response.status_code == 422
#     assert "user_id" in response.text

#     # Test case for missing longitude and latitude
#     response = client.post("/feedmanager", json={"feed_data": {"user_id": "valid_object_id"}, "api_key": "valid_api_key"})
#     assert response.status_code == 422
#     assert "Longitude and latitude" in response.text

#     # Test case for invalid longitude format
#     response = client.post("/feedmanager", json={"feed_data": {"user_id": "valid_object_id", "longitude": "invalid", "latitude": 0.0}, "api_key": "valid_api_key"})
#     assert response.status_code == 400
#     assert "Invalid longitude" in response.text

#     # Test case for invalid latitude format
#     response = client.post("/feedmanager", json={"feed_data": {"user_id": "valid_object_id", "longitude": 0.0, "latitude": "invalid"}, "api_key": "valid_api_key"})
#     assert response.status_code == 400
#     assert "Invalid latitude" in response.text

#     # Test case for out-of-range longitude
#     response = client.post("/feedmanager", json={"feed_data": {"user_id": "valid_object_id", "longitude": 190.0, "latitude": 0.0}, "api_key": "valid_api_key"})
#     assert response.status_code == 400
#     assert "Longitude format is invalid" in response.text

#     # Test case for out-of-range latitude
#     response = client.post("/feedmanager", json={"feed_data": {"user_id": "valid_object_id", "longitude": 0.0, "latitude": 100.0}, "api_key": "valid_api_key"})
#     assert response.status_code == 400
#     assert "Latitude format is invalid" in response.text
