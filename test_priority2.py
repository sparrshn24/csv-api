import pytest
from priority2 import app


@pytest.fixture
def client():
    with app.test_client() as cli:
        yield cli


# def test_generate_utterances_valid_input(client):
#     list_of_indices = "1,2,3"
#     number_of_generated_utterances = 3

#     # response = app.test_client().post(
#     #     f"/api/generate/like={list_of_indices}&count={number_of_generated_utterances}")

#     url = f"http:localhost:5001/api/generate/like={list_of_indices}&count={number_of_generated_utterances}"
#     response = client.post(url)

#     # with app.test_request_context():
#     #     url = url_for("generate_utterances",
#     #                   list_of_indices=list_of_indices,
#     #                   number_of_generated_utterances=number_of_generated_utterances)

#     # response = client.post(url, headers={"Content-Type": "application/json"})
#     assert response.status_code == 200
#     assert response.json == {'message': 'Request completed.'}
#     # Add additional assertions to check the generated data or any other expected behavior


def test_generate_utterances_single_index(client):
    list_of_indices = "1"
    number_of_generated_utterances = 3

    response = client.post(
        f"/api/generate/like={list_of_indices}&count={number_of_generated_utterances}")
    assert response.status_code == 200
    assert response.json == {'message': 'Request completed.'}
    # Add additional assertions to check the generated data or any other expected behavior


def test_generate_utterances_out_of_range_index(client):
    list_of_indices = "1005,2005,3005"
    number_of_generated_utterances = 2

    response = client.post(
        f"/api/generate/like={list_of_indices}&count={number_of_generated_utterances}")
    assert response.status_code == 400
    assert response.json == {
        'error': 'Index 1005 is out of range for the DataFrame.'}
    # Add additional assertions to check the error response or any other expected behavior


def test_generate_utterances_invalid_indices(client):
    list_of_indices = "1,a,3"
    number_of_generated_utterances = 4

    response = client.post(
        f"/api/generate/like={list_of_indices}&count={number_of_generated_utterances}")
    assert response.status_code == 400
    assert response.json == {
        'error': 'Failed to convert indices of the intents to be added. Ensure they are separated by commas if multiple.'}


# def test_generate_utterances_invalid_input(client):
#     response = client.post("/api/generate/like=&count=")
#     assert response.status_code == 400
#     assert response.json == {
#         'error': 'Indices passed should be enclosed in {} separated by commas if multiple, or enclosed in {} if only one.'}
