import os
import openai
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from flask_cors import CORS
from datetime import datetime

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

@app.route('/get-portfolio-opinion', methods=['POST'])

@app.route('/get-portfolio-explanation', methods=['POST'])
# Run the token suggestion
@app.route('/get-portfolio-generation', methods=['POST'])
def get_token_suggestion():
    data = request.json
    age = data['age']
    income = data['income']
    risk_score = data['risk_score']
    # find an inudustry standard way of understanding risk. 

    # OpenAI interaction
    system_message = {
        "role": "system",
        "content": "You are a financial expert who provides insightful analyses and opinions to create crypto portfolios."
    }
        
    user_message = {
        "role": "user",
        "content": f"""
        Build a crypto portfolio for a client with the following qualities, with this real time price data. 
        Client information:
        - Age: {age}
        - Income: {income}
        - Risk Score: {risk_score}

        Real time price data:

        Considering these factors and other market dynamics, 
        carefully incorporate the 
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
