import json
import re
import pandas as pd
from flask import Flask, request, jsonify


DATA = 'data.csv'

app = Flask(__name__)


def read_file(file):
    try:
        data_frame = pd.read_csv(file, dtype={'Index': int})
        return data_frame
    except FileNotFoundError:
        return jsonify({'error': 'CSV not found'}), 404
    except pd.errors.ParserError:
        return jsonify({'error': 'Invalid format'}), 400


def validate_utterance(input_utter):
    if not isinstance(input_utter, str):
        return jsonify(error='Utterance must be a string'), 400

    if not input_utter:
        return jsonify(error='Utterance field cannot be empty'), 400

    filtered_utterance = re.sub(
        r'[^a-zA-Z\s\.,!?"\']', '', input_utter)

    filtered_utterance = filtered_utterance.strip().replace('"', '')
    if not filtered_utterance:
        return jsonify(error='Utterance must only contain letters or punctuations'), 400

    return input_utter


@app.errorhandler(415)
def handle_415_error(e):
    return jsonify({'error': 'Unsupported Media Type. Payload should only be JSON'}), 415


@app.errorhandler(405)
def handle_delete_error(err):
    return jsonify(error='DELETE method not allowed'), 405

# Error handler for PATCH method not allowed


@app.errorhandler(405)
def handle_patch_error(error):
    return jsonify(error='PATCH method not allowed'), 405


@app.errorhandler(400)
def handle_bad_request(error):
    return jsonify(error='Payload not structured correctly'), 400


@ app.route("/api/data", methods=['GET', 'POST'])
def read_or_modify_data():
    if request.method == 'GET':
        try:
            data = pd.read_csv(DATA).values.tolist()
            return data
        except FileNotFoundError:
            return jsonify(error="File not found. Please check the file path."), 404
        except pd.errors.ParserError:
            return jsonify(error="Error while parsing the CSV file."), 400
    elif request.method == 'POST':
        try:

            new_data = request.json
            print(new_data)
            if 'Utterance' not in new_data:
                return jsonify(error='Invalid payload. Field "Utterance" is missing'), 400

            if not new_data.get('Utterance') and not new_data.get("Utterance"):
                return jsonify(error='Utterance does not have a value. Cannot be blank'), 400

            new_utterance = validate_utterance(new_data.get('Utterance'))

            data_frame = read_file(DATA)

            new_index = data_frame.shape[0]+1

            new_row = pd.DataFrame(
                {'Index': [new_index], 'Utterance': [new_utterance]})

            new_dataframe = pd.concat(
                [data_frame, new_row], ignore_index=True)

            new_dataframe.to_csv('data.csv', index=False)

            return {'message': 'Data adding successful.'}
        except json.JSONDecodeError:
            return jsonify(error='Payload can only be JSON'), 400
        except ValueError:
            return jsonify(error='Value error occurred.'), 400


@ app.route("/api/data/old=<index_to_be_patched>", methods=["PATCH"])
def patch_data(index_to_be_patched):
    if not re.match(r'^\d+$', index_to_be_patched):
        return jsonify({'error': 'Invalid index format. Index must be a single integer.'}), 400
    try:
        data_frame = read_file(DATA)
        index_to_be_patched = int(index_to_be_patched)
        if index_to_be_patched < 0 or index_to_be_patched > (data_frame.shape[0]-1):
            return jsonify({'error': 'Invalid index provided. Please enter correct index.'}), 400
        json_data = request.json
        new_utter = json_data['New_Utterance']
        new_utter = validate_utterance(new_utter)
        data_frame.loc[index_to_be_patched, 'Utterance'] = new_utter
        data_frame.to_csv('data.csv', index=False)
        return {'message': 'Data patched successfully'}
    except KeyError:
        return jsonify({'error': 'New_Utterance key missing. Please specify'
                        ' New_Utterance as a key in a'
                        ' JSON format'}), 400
    except TypeError:
        return jsonify({'error': 'Invalid payload. Request body should be '
                        'a valid JSON object'}), 400


@ app.route("/api/data/index=<index_to_be_deleted>", methods=['DELETE'])
def delete_data(index_to_be_deleted):
    data_frame = read_file(DATA)

    if not re.match(r'^\d+$', index_to_be_deleted):
        return jsonify({'error': 'Invalid index format. Index must be a single integer.'}), 400
    index_to_be_deleted = int(index_to_be_deleted)
    if index_to_be_deleted < 0 or index_to_be_deleted > (data_frame.shape[0]):
        return jsonify({'error': 'Index out of bounds. Please enter correct index.'}), 400
    else:
        rows_to_drop = data_frame[data_frame['Index']
                                  == index_to_be_deleted]
        data_frame.drop(rows_to_drop.index, inplace=True)
    data_frame.to_csv('data.csv', index=False)
    return {'message': 'Data deleted successfully'}


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
