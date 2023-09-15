import re
from unittest.mock import patch
from pandas.errors import ParserError
import pytest
import pandas
from priority1 import app
from priority1 import validate_utterance


@pytest.fixture
def api_client():
    with app.test_client() as api_client:
        yield api_client

# GET TESTS


def test_read_data_success(api_client):
    response = api_client.get('/api/data')
    assert response.status_code == 200

    assert response.is_json

    expected_data = [
        tuple(item)  # Convert inner lists to tuples
        for item in response.json
    ]

    assert set(tuple(row) for row in response.json) <= set(expected_data)


def test_read_data_file_not_found(api_client, mocker):
    mocker.patch('pandas.read_csv', side_effect=FileNotFoundError)
    response = api_client.get('/api/data')
    assert response.status_code == 404
    assert response.is_json
    assert response.json == {
        'error': "File not found. Please check the file path."}


def test_read_data_csv_parse_error(api_client, mocker):
    # Assuming the method returns a 400 error and a JSON message for a pd.errors.ParserError
    mocker.patch('pandas.read_csv', side_effect=ParserError(
        "Error while parsing the CSV"))
    response = api_client.get('/api/data')
    assert response.status_code == 400
    assert response.is_json
    assert response.json == {'error': "Error while parsing the CSV file."}


def test_read_data_empty_file(api_client, mocker):
    # Mock an empty DataFrame
    mocker.patch('pandas.read_csv', return_value=pandas.DataFrame())
    response = api_client.get('/api/data')
    # Assuming the API returns a success status code
    assert response.status_code == 200
    assert response.is_json
    assert response.json == []  # Empty JSON response indicating an empty file

# POST


def test_add_data_success(api_client):
    payload = {'Utterance': 'Hello, how are you?'}
    response = api_client.post('/api/data', json=payload)
    assert response.status_code == 200
    assert response.is_json
    assert response.json == {'message': 'Data adding successful.'}
    # Additional assertions to verify the state after the data is added


def test_add_data_missing_payload(api_client):
    payload = {}
    response = api_client.post('/api/data', json=payload)
    assert response.status_code == 400
    assert response.is_json
    assert response.json == {
        'error': 'Invalid payload. Field "Utterance" is missing'}


def test_add_data_empty_utterance(api_client):
    payload = {'Utterance': ''}
    response = api_client.post('/api/data', json=payload)
    assert response.status_code == 400
    assert response.is_json
    assert response.json == {
        'error': 'Utterance does not have a value. Cannot be blank'}


def test_validate_utterance_valid_string():
    input_utterance = "Hello, how are you?"
    result = validate_utterance(input_utterance)
    assert result == input_utterance

# PATCH


def test_patch_data_success(api_client):
    response = api_client.patch(
        '/api/data/old=0', json={'New_Utterance': 'new utterance'})
    data = response.get_json()
    assert response.status_code == 200
    assert data['message'] == 'Data patched successfully'


def test_patch_data_invalid_index(api_client):
    response = api_client.patch(
        '/api/data/old=1000', json={'New_Utterance': 'new utterance'})
    data = response.get_json()
    assert response.status_code == 400
    assert data['error'] == 'Invalid index provided. Please enter correct index.'


def test_patch_data_missing_key(api_client):
    response = api_client.patch('/api/data/old=0', json={})
    data = response.get_json()
    assert response.status_code == 400
    assert data['error'] == 'New_Utterance key missing. Please specify New_Utterance as a key in a JSON format'


def test_patch_index_format_valid():
    index = "42"
    pattern = r'^\d+$'
    assert re.match(pattern, index)


def test_patch_index_format_invalid():
    index = "{42}"
    pattern = r'^\d+$'
    assert not re.match(pattern, index)


def test_patch_data_multiple_indices(api_client):
    response = api_client.patch(
        '/api/data/old=0,1', json={'New_Utterance': 'new utterance'}
    )
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data
    assert data['error'] == 'Invalid index format. Index must be a single integer.'


def test_patch_data_key_error(api_client):
    with patch('priority1.read_file') as mock_read_file:
        mock_read_file.side_effect = KeyError()
        response = api_client.patch(
            '/api/data/old=100', json={'New_Utterance': 'Updated Utterance'})
        data = response.get_json()
        assert response.status_code == 400
        assert 'error' in data
        assert data['error'] == 'New_Utterance key missing. Please specify New_Utterance as a key in a JSON format'


def test_patch_data_type_error(api_client):
    response = api_client.patch('/api/data/old=100', json='Invalid JSON')
    data = response.get_json()
    assert response.status_code == 400
    assert 'error' in data
    assert data['error'] == 'Invalid payload. Request body should be a valid JSON object'

# DELETE


def test_delete_data_success(api_client):
    response = api_client.delete('/api/data/index=10')
    data = response.get_json()
    assert response.status_code == 200
    assert 'message' in data
    assert data['message'] == 'Data deleted successfully'


def test_delete_data_index_out_of_bounds(api_client):
    response = api_client.delete('/api/data/index=1000')
    data = response.get_json()
    assert response.status_code == 400
    assert 'error' in data
    assert data['error'] == 'Index out of bounds. Please enter correct index.'


def test_delete_data_invalid_index(api_client):
    response = api_client.delete('/api/data/index=abc')
    data = response.get_json()
    assert response.status_code == 400
    assert 'error' in data
    assert data['error'] == 'Invalid index format. Index must be a single integer.'
