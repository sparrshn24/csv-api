import os
import openai
import pandas as pd
from flask import Flask, jsonify
openai.api_key = os.getenv('OPENAI_API_KEY')

app = Flask(__name__)

DATA = 'data.csv'


def read_file(file):
    try:
        data_frame = pd.read_csv(file, dtype={'Index': int})
        return data_frame
    except FileNotFoundError:
        return jsonify({'error': 'CSV not found'}), 404
    except pd.errors.ParserError:
        return jsonify({'error': 'Invalid format'}), 400


@app.route("/api/generate/like=<list_of_indices>&count=<number_of_generated_utterances>", methods=["POST"])
def generate_utterances(list_of_indices, number_of_generated_utterances):
    try:
        if isinstance(list_of_indices, str):
            if "," in list_of_indices:
                list_of_indices = [int(index)
                                   for index in list_of_indices.split(",")]
            else:
                list_of_indices = [int(list_of_indices)]

        if list_of_indices == '' or number_of_generated_utterances == '':
            return jsonify({'error': 'At least one parameter is empty'}), 400

        if "," in number_of_generated_utterances:
            return jsonify({'error': 'Multiple values for count are not allowed.'}), 400

        if int(number_of_generated_utterances) > 6 or len(list_of_indices) > 5:
            return jsonify({'error': 'Not more than 6 similar utterance generations and at most similarity check between 4 indices'
                            ' at a time mindful of API costs'}), 400
        list_of_strings = []
        data_frame = read_file(DATA)

        for index in list_of_indices:
            if index >= data_frame.shape[0]:
                return jsonify({'error': f'Index {index} is out of range for the DataFrame.'}), 400
            utter = data_frame.iloc[index]['Utterance']
            list_of_strings.append(utter)

        # print(list_of_strings)

        sentence = '\n'.join(list_of_strings)
        # print(sentence)

        prompt = f"Following are a list of intent strings: {sentence}. Can you create {number_of_generated_utterances} more intent strings similar in context to these but do not include anything else in the answer apart from these strings. Also, separate the strings with a ',' separator. I repeat the answer should only include the {number_of_generated_utterances} strings separated by commas and nothing else."
        # print(prompt)

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=30,  # Adjust the value based on the length of the expected response
        )
        # print(utterances)
        sentence = response['choices'][0]['message']['content']

        utterances = sentence.split('\n')
        # print(list_utterances)
        list_utterances = []
        for split_utter in utterances:
            if split_utter.strip():
                list_utterances.append(split_utter.strip())
        new_rows = []
        start_index = data_frame.shape[0]
        count = 0
        for utterance in list_utterances:
            count += 1
            print(utterance)
            new_row = {'Index': start_index+count,
                       'Utterance': utterance.replace('"', '')}
            new_rows.append(new_row)

        new_data_frame = pd.DataFrame(new_rows)
        data_frame = pd.concat(
            [data_frame, new_data_frame], ignore_index=True)

        data_frame.to_csv('data.csv', index=False)

        return {'message': 'Request completed.'}

    except ValueError:
        return jsonify({'error': 'Failed to convert indices of the intents to be added. Ensure they are separated by commas if multiple.'}), 400


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5001)
