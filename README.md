# csv-api

## REST API with Chat-GPT Integration
This repository contains a REST API implemented in Python 3.9.10 using the Flask-RESTX framework. The API serves the purpose of managing a list of training phrases typically used in Natural Language Processing (NLP) intent recognition. It also integrates with OpenAI's Chat-GPT to generate similar utterances and appends them to the training data.

### Requirements
To run this API, you will need the following libraries:

- Flask-RESTX
- NumPy
- Pandas
Ensure you have Python 3.9.10 installed on your system.

### Getting Started
Follow these steps to set up and run the API:

Clone this repository to your local machine.
Install the required libraries using pip install -r requirements.txt.
Create a virtual environment (optional but recommended).
Run the API using python app.py.
By default, the API runs on http://localhost:5000.

### API Endpoints
1. Training Phrases
GET /phrases: Retrieve the list of training phrases.
POST /phrases: Add a new training phrase.
PATCH /phrases/{phrase_id}: Update an existing training phrase.
DELETE /phrases/{phrase_id}: Delete a training phrase by its ID.
2. Chat-GPT Integration
POST /generate: Generate new utterances using Chat-GPT and append them to the training data.
Usage
To interact with the API, you can use tools like Postman.
