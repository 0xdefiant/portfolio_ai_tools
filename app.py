import os
import openai
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from flask_cors import CORS
import requests

load_dotenv()  # Load environment variables from .env file

app = Flask(__name__)
CORS(app)

# Retrieve the API key from environment variables
openai.api_key = os.getenv('OPENAI_API_KEY')

@app.route('/')
def home():
    return render_template('home/index.html')

@app.route('/get-portfolio-suggestion', methods=['POST'])
def get_portfolio_suggestion():
    data = request.json
    network = data['network']
    tokens = data['tokens']
    
    # Fetch data from Geckoterminal
    url = f'https://api.geckoterminal.com/api/v2/networks/{network}/tokens/{tokens}?include=include'
    gecko_response = requests.get(url, headers={'accept': 'application/json'})

    if gecko_response.status_code != 200:
        return jsonify({"error": f"Failed to fetch data from Geckoterminal: {gecko_response.content}"}), 500
    
    token_data = gecko_response.json()

    # Extract relevant info from Geckoterminal's response
    token_name = token_data['data']['attributes']['name']
    token_price_usd = token_data['data']['attributes']['price_usd']
    token_symbol = token_data['data']['attributes']['symbol']
    token_volume_24h = token_data['data']['attributes']['volume_usd']['h24']
    total_supply = token_data['data']['attributes']['total_supply']

    # Create the message for the OpenAI model
    message = {
        "role": "system",
        "content": "You are a crypto portfolio allocation specialist, that builds portfolio models from information that you are given."
    }
    user_message = {
        "role": "user",
        "content": f"I'm considering {token_name} ({token_symbol}). It's currently priced at ${token_price_usd} with a 24h trading volume of ${token_volume_24h}, and supply of {total_supply}. Given this, how should I structure my portfolio?"
    }

    openai_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[message, user_message]
    )

    ai_response = openai_response.choices[0].message['content']
    return jsonify({"portfolio": ai_response})

if __name__ == '__main__':
    app.run(port=5000)
