AI Portfolio Generator and Financial Summary Tool
Description
This application is designed to provide two main features for financial advisors and clients:

AI Portfolio Generation: Based on risk frameworks of clients or firm-wide standards, the app generates customized investment portfolios using AI.
Client Financial Portfolio Summarizing Tool: It generates a concise, easy-to-understand PDF summary of a client's financial portfolio.
Features
AI-driven portfolio creation considering client-specific risk profiles.
Automated summarization of financial portfolios into client-friendly PDF reports.
Integration with real-time market data for accurate financial analysis.
Technologies
Python with Flask for backend services.
OpenAI API for AI-driven insights and summaries.
Moralis API for real-time cryptocurrency data.
React (suggested) for front-end implementation.
Installation
Clone the repository to your local machine.
Install dependencies using pip install -r requirements.txt.
Usage
Starting the Server: Run python app.py to start the Flask server.
Generating Portfolios:
Send a POST request to /portfolio_create with the client's data (age, income, risk score, etc.).
The server returns a JSON object with a tailored investment portfolio.
Summarizing Portfolios:
Send a POST request to /summarize_pdf with the client's portfolio data.
The server returns a PDF report summarizing the portfolio in an understandable format.
API Reference
/portfolio_create: POST request to generate a customized investment portfolio.
/summarize_pdf: POST request to create a summarized PDF report of a client's portfolio.
Environment Variables
OPENAI_API_KEY: API key for OpenAI.
MORALIS_API_KEY: API key for Moralis service.
Contributing
Contributions are welcome. Please open an issue first to discuss what you would like to change or add.

License
