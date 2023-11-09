from datetime import datetime
from fpdf import FPDF
import re
import json


token_list = {
    "bitcoin": "bitcoin",
    "ethereum": "ethereum",
    "lido-staked-ether": "staked-ether",
    "solana": "solana",
    "ripple": "ripple",
    "uniswap": "uniswap",
    "polkadot": "polkadot",
    "avalanche-2": "avalanche-2",
    "chainlink": "chainlink",
    "optimism": "optimism",
    "arbitrum": "arbitrum",
    "matic": "matic-network",
    "axie-infinity": "axie-infinity",
    "decentraland": "decentraland",
    "maker": "maker",
}

# For @app.route('/portfolio_create', methods=['POST']) # Generates Portfolio from desired attributes 
def generate_dates():
    today = datetime.now()
    # six_month_ago = today - timedelta(days=30*6)  # Approximating a month as 30 days for simplicity

    # Formatting dates as strings
    date_strings = [
        today.strftime('%d-%m-%Y'),
        # six_month_ago.strftime('%d-%m-%Y'), <-- use something like this if want to generate for other dates
    ]
    return date_strings
dates_list = generate_dates()

def extract_json(response_text):
    keyword = "3. Based on the above recommendations"
    index = response_text.find(keyword)
    if index != -1:
        truncated_text = response_text[index:]

        pattern = r'\{.*?\}'
        matches = re.findall(pattern, truncated_text, re.DOTALL)
        
        if matches:
            for match in matches:
                try:
                    json_obj = json.loads(match)
                    return json_obj
                except json.JSONDecodeError:
                    continue
            return {"error": "Found possible JSON objects but none could be decoded."}
        else:
            return {"error": "No JSON object found in the provided text."}
    else:
        return {"error": f"Keyword '{keyword}' not found in the provided text."}
    
def extract_reason(response_text):
    keyword = "3. Based on the above recommendations"
    index = response_text.find(keyword)
    if index != -1:
        return response_text[:index].strip()
    else:
        return "Keyword not found, couldn't extract first part."




# For @app.route('/summarize_pdf', methods=['POST']) # Handles a API response from by all accounts GET positions
def organize_data(response_data):
    objects_by_type = {}
    if 'data' not in response_data or not isinstance(response_data['data'], list):
        raise ValueError("Invalid data format")
    
    # Separate the objects and store them by "secType" and create dictionary within the "secType" by the name of the asset
    for obj in response_data['data']:
        sec_type = obj['secType']
        if sec_type not in objects_by_type:
            objects_by_type[sec_type] = {}
        
        investment_name = obj['name']
        objects_by_type[sec_type][investment_name] = obj
    return objects_by_type

def create_pdf(text, user_id):
    timestamp = datetime.now().strftime("%H%M%S")
    output_filename = f"{user_id}_{timestamp}.pdf"
    class PDF(FPDF):
        def header(self):
            self.set_font("Arial", 'B', 12)
            self.cell(0, 10, "Steward AI report", 0, 1, 'C')
        
        def footer(self):
            self.set_y(-15)
            self.set_font("Arial", 'I', 8)
            self.cell(0, 10, f"Page {self.page_no()}", 0, 0, 'C')

    pdf = PDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.set_font("Arial", style='B', size=16)
    pdf.cell(0, 10, "Your Portfolio Summary", ln=True, align='C')

    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, text)

    pdf.set_text_color(220, 50, 50)
    pdf.cell(0, 10, "Disclaimer", ln=True)

    pdf.output(f"testPDF/{output_filename}")

def get_stock_data(data):
    sorted_data = dict(sorted(data.items(), key=lambda item: item[1]['name']))
    valuable_data = {
        key: {
            'ticker': value['ticker'],
            'name': value['name'],
            'units': value['units'],
            'unitPrice': value['unitPrice']['amount'],
            'marketValue': value['marketValue']['amount'],
            'sectorCodeName': value['sectorCodeName']
        } 
        for key, value in sorted_data.items()
    }
    return valuable_data

def get_mutual_fund_data(data):
    sorted_data = dict(sorted(data.items(), key=lambda item: item[1]['name']))
    valuable_data = {
        key: {
            'ticker': value['ticker'],
            'name': value['name'],
            'costBasis': value['costBasis']['amount'],
            'marketValue': value['marketValue']['amount'],
            'bondStyleBoxLongName': value['bondStyleBoxLongName'],
            'assetAllocationUSStock': value['assetAllocationUSStock'],
            'assetAllocationNonUSStock': value['assetAllocationNonUSStock'],
            'assetAllocationUSBond': value['assetAllocationUSBond'],
            'assetAllocationNonUSBond': value['assetAllocationNonUSBond'],
            'currencyCode': value['marketValue']['currencyCode']
        } 
        for key, value in sorted_data.items()
    }
    return valuable_data