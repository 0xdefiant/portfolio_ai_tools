import os
import openai
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from flask_cors import CORS
from datetime import datetime
from fpdf import FPDF

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
class PDF(FPDF):
    def header(self):
        # You can set a custom header here if needed
        pass

    def footer(self):
        # Page number at the bottom
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, 'Page ' + str(self.page_no()), 0, 0, 'C')
# Run the token suggestion
def get_portflolio_explanation():
    # ByAllAccounts pdf generator
    
    def string_to_pdf(text, output_filename="output.pdf"):
        pdf = PDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, text)
        pdf.output(output_filename)


@app.route('/get-portfolio-generation', methods=['POST'])
def get_portfolio_suggestion():
    data = request.json
    age = data['age']
    income = data['income']
    risk_score = data['risk_score']
    # some stocks or funds to choose from?
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
