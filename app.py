import os
import openai
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from flask_cors import CORS
from datetime import datetime
from moralis import evm_api

load_dotenv()  # Load environment variables from .env file

app = Flask(__name__)
CORS(app)

# Retrieve the API key from environment variables
openai.api_key = os.getenv('OPENAI_API_KEY')
api_key = "MORALIS_API_KEY"
current_date_string = str(datetime.now().isoformat())


@app.route('/')
def home():
    return render_template('home/index.html')

# Run the token suggestion
@app.route('/get-token-suggestion', methods=['POST'])
def get_token_suggestion():
    data = request.json
    age = data['age']
    income = data['income']
    risk_score = data['risk_score']
    chain = data['chain']
    
    # Placeholder for the top tokens and their addresses. Update as needed.
    token_list = {
    "WBTC": "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599",
    "WETH": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
    "UNI": "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984",
    "stETH": "0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84",
    "wBNB": "0xB8c77482e45F1F44dE1745F52C74426C631bDD52",
    "MATIC": "0x7D1AfA7B718fb893dB30A3aBc0Cfc608AaCfeBB0",
    "LINK": "0x514910771AF9Ca656af840dff83E8264EcF986CA",
    "LDO": "0x5A98FcBEA516Cf06857215779Fd812CA3beF1B32",
    "MKR": "0x9f8F72aA9304c8B593d555F12eF6589cC3A579A2",
    "cETH": "0x4Ddc2D193948926D02f9B1fE9e1daa0718270ED5"
    }

    historicalPrice = {}

    # Getting the current date as a datestring in ISO 8601 format
    current_date_string = datetime.now().isoformat()

    params = {
        "chain": "eth",
        "date": current_date_string
    }
    result = evm_api.block.get_date_to_block(
        api_key=api_key,
        params=params,
    )
    currentBlock = result['block']

    for token, address in token_list.items():
        params = {
            "chain": f"{chain}",
            "include": "percent_change",
            "address": f"{address}",
            "to_block": currentBlock
        }
        result = evm_api.token.get_token_price(
            api_key=api_key,
            params=params,
        )

        historicalPrice[token] = {
            'name': result['tokenName'],
            'tokenLogo': result['tokenLogo'],
            'decimals': result['tokenDecimals'],
            'price_usd': float(result['usdPrice']),
            'percent_change_24hr': float(result['24hrPercentChange']),
            'tokenAddress': result['tokenAddress'],
            'toBlock': result['toBlock']
        }

    # OpenAI interaction
    system_message = {
        "role": "system",
        "content": "You are a cryptocurrency expert who provides insightful analyses and opinions to create crypto portfolios."
    }
    
    token_data = "\n".join([f"{token}: ${details['price_usd']} (24hr change: {details['percent_change_24hr']}%)" for token, details in historicalPrice.items()])
    
    user_message = {
        "role": "user",
        "content": f"""
        Build a crypto portfolio for a client with the following qualities, with this real time price data. 
        Client information:
        - Age: {age}
        - Income: {income}
        - Risk Score: {risk_score}

        Real time price data:
        {token_data}

        Considering these factors and other market dynamics, 
        would you recommend incorporating these tokens into the client's portfolio?
    """
    }

    openai_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[system_message, user_message]
    )

    ai_response = openai_response.choices[0].message['content']
    return jsonify({"portfolio": ai_response})

if __name__ == '__main__':
    app.run(port=5000)
