import os
import openai
import json
import requests
import pprint
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from flask_cors import CORS
from datetime import datetime
from utils.functions.utils import token_list, dates_list, extract_json, extract_reason, organize_data, get_stock_data, get_mutual_fund_data, create_pdf

load_dotenv() # Load Environment variables from .env file

app = Flask(__name__)
CORS(app)

openai.api_key = os.getenv('OPENAI_API_KEY')
api_key = os.getenv('MORALIS_API_KEY')
current_date_string = datetime.now().strftime('%d-%m-%Y')

# @app.route('/get_positions_and_summarize_pdf')


@app.route('/summarize_pdf', methods=['POST']) # Handles a API response from by all accounts GET positions
def generate_summary():
    try:
        # Assuming the data is being sent as a JSON object in the body of a POST request
        response_data = request.get_json()
        user_id = "user123" # will need to track the request to a user therefore, we will get a user_id variable somehow.
        objects_by_type = organize_data(response_data)
        # print(f"Object: {objects_by_type}")
        # { 'secType' - i.e MF, Stock, etc... { 'assetName' -- ie Tesla, AT&T, MutualFund xyz etc... { 'AssetAttributes': 'value' }}}
        # Anthony, once you are able to find the structure for different asset type respones, assign variables to the important data points.

        def sort_data_by_asset_class(objects_by_type):
            sorted_data = {}
            for asset_class, data in objects_by_type.items():
                if asset_class == 'Mutualfund':
                    sorted_data[asset_class] = get_mutual_fund_data(data)
                elif asset_class == 'Stock':
                    sorted_data[asset_class] = get_stock_data(data)
                else:
                    # For other asset classes, keep data as is, or implement additional sorting functions
                    sorted_data[asset_class] = data
            return sorted_data
        
        # valuable_stock_data = get_stock_data(objects_by_type['Stock']) # This is the object for all of the stocks, no use here just to test
        # pprint.pprint(f"VALUABLE STOCK: {valuable_stock_data}")
        # Now you have the relevant data and can proceed with whatever processing you need
        result_data = sort_data_by_asset_class(objects_by_type)
        pprint.pprint(f"LOOK HERE: {result_data}")

        openai_prompt = f"""
            I am going to give you a list of my investments, I want you to summarize the content of each of my investments
            I will give you each investment by type, attributes and market value.

            Holdings data:
            {result_data}

            From this information, summarize what each of my investments are as if I did not have a deep understanding of financial markets. 
            Give a 3-5 sentence clear and concise summary about each investment.
            """
        system_message = {
            "role": "system",
            "content": "You are a financial writer that summarizes client portfolio's"
        }
        
        user_message = {
            "role": "user",
            "content": openai_prompt
        }

        openai_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[system_message, user_message]
        )

        ai_response = openai_response.choices[0].message['content']
        print(ai_response)
        
        created_pdf = create_pdf(ai_response, user_id) # Have a userID as the name of the pdf, so that we can find it in the pdf directory.
        
        return jsonify({"status": ai_response, "pdf": created_pdf})
    
    except Exception as e:
        return jsonify({"error": f"Error: {str(e)}"})


@app.route('/portfolio_create', methods=['POST']) # Generates Portfolio from desired attributes and 
def generate_portfolio():
    try:
        data = request.json
        print("Received Data from Client:", data)
        age = data['age'] # these are easily adjustable
        income = data['income']
        risk_score = data['risk_score']
        crypto_age = data['timeInCrypto']
        agression = data['aggression'] 


        def fetch_historical_price(token_list, dates_list):
            historicalPrice = {}

            print("Tokens for selected chain:", token_list)

            for token, id in token_list.items():
                for date in dates_list:
                    url = f"https://api.coingecko.com/api/v3/coins/{id}/history?date={date}&localization=false"
                    response = requests.get(url)
                    if response.status_code == 200:
                        data = response.json()
                        try:
                            data_point = {
                                'price_usd': round(float(data['market_data']['current_price']['usd']), 4),
                                'market_cap_usd': round(float(data['market_data']['market_cap']['usd']), 4),
                                'total_volume_usd': round(float(data['market_data']['total_volume']['usd']), 4),
                                'date': date  # Added to distinguish data points by date
                            }
                            # Create a list for the token if it doesn't exist in historicalPrice
                            if token not in historicalPrice:
                                historicalPrice[token] = []
                            historicalPrice[token].append(data_point)
                        except Exception as e:
                            print(f"Error getting data for {token} on {date}: {e}")
                    else:
                        print(f"Error fetching data for {token} on {date}: {response.status_code}")

            return historicalPrice
        
        historical_data = fetch_historical_price(token_list, dates_list)
        historicalPrice_str = json.dumps(historical_data, indent=2)
        formatted_output = f"Data: {historicalPrice_str}"
        print(f"FORMATTED DATA: {formatted_output}")


        json_example = {
                "token1": "30%",
                "token2": "15%",
                "token3": "10%",
                "etc...": "x%"
            }

        openai_prompt = f"""
            Construct a customized crypto portfolio tailored to the specific needs of a financial advisor. The portfolio should be based on both the advisor's personal attributes and the current market data provided below.
            **Advisor Attributes:**
            - Age: {age},
            - Income: {income},
            - Risk Score (1 is low-risk, 10 is high-risk): {risk_score},
            - Time in Crypto (years): {crypto_age},
            - Investment Aggression (1 is low-risk, 10 is high-risk): {agression}

            **Real-time USD Price, Market Cap, and Total Volume Data:**
            {formatted_output}

            Return your answer in three sections:
            1. Begin with a generalized disclosure statement such as, "1. Please note that cryptocurrency investments are subject to various risks..."
            2. Next, provide a reasoned portfolio, starting with "2. Considering the advisor's attributes and real-time market data, the portfolio is as follows..."
            3. Conclude by offering a JSON-formatted breakdown of the portfolio. Start this section with "3. Based on the above recommendations, the portfolio breakdown is..." and provide the JSON object. 
            Here is an example of the JSON formating to use:
            {json_example}
            """
        # OpenAI interaction
        system_message = {
            "role": "system",
            "content": "You are a cryptocurrency expert who provides insightful analyses and opinions to create crypto portfolios."
        }
        
        user_message = {
            "role": "user",
            "content": openai_prompt
        }

        openai_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[system_message, user_message]
        )

        ai_response = openai_response.choices[0].message['content']
        print(f"ORIGINAL OPENAI: {ai_response}")
        reason_data = extract_reason(ai_response)
        print(f"REASONING: {reason_data}")
        json_data = extract_json(ai_response)
        if "error" in json_data:
            return jsonify({"error": json_data["error"]})
        print(f"JSON OBJECT: {json_data}")
        return jsonify({"portfolio": json_data, "reason": reason_data})
    except Exception as e:
        return jsonify({"error": f"Error: {str(e)}"})
    


if __name__ == '__main__':
    app.run(debug=True, port=5000)  # Choose a port that doesn't conflict with regular Steward App