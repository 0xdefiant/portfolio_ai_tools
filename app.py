import os
import openai
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
import requests

load_dotenv()  # Load environment variables from .env file

app = Flask(__name__)

# Retrieve the API key from environment variables
openai.api_key = os.getenv('OPENAI_API_KEY')

@app.route('/')
def home():
    return render_template('home/index.html')

@app.route('/get_token_data', methods=['GET'])
def get_token_data():
    network = request.form['network']
    token_address = request.form['tokens']
    url = f'https://api.geckoterminal.com/api/v2/networks/{network}/tokens/multi/{token_address}'
    response = requests.get(url, headers={'accept': 'application/json'})
    print(f"Gecko API Response Code: {response.status_code}")  
    if response.status_code == 200:
        return jsonify(response.json())
    else:
        print(f"Error Message: {response.content}") 
        return jsonify({'error': 'Unable to fetch data'}), response.status_code

@app.route('/get-trade', methods=['POST'])
def get_trade():
    data = request.json
    holdings = data.get('holdings', [])

    # Convert list of cryptocurrencies into a string for the prompt
    holdings_str = ", ".join(holdings)

    message = {
        "role": "system",
        "content": "You are a crypto portfolio allocation specialist, that builds portfolio models from information that you are given."
    }
    user_message = {
        "role": "user",
        "content": f"I have the following cryptocurrencies: {holdings_str}. Please create a model portfolio."
    }

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[message, user_message]
    )

    # Get the AI's response
    ai_response = response.choices[0].message['content']

    return jsonify({"portfolio": ai_response})


if __name__ == '__main__':
    app.run(port=5000)
