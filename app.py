import os
import openai
from flask import Flask, request, jsonify, redirect, render_template, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from dotenv import load_dotenv
from flask_cors import CORS
from datetime import datetime
from fpdf import FPDF
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
CORS(app)
app.secret_key = 'mysecretkey'

# Retrieve the API key from environment variables
openai.api_key = os.getenv('OPENAI_API_KEY')
api_key = "MORALIS_API_KEY"
current_date_string = str(datetime.now().isoformat())
load_dotenv()  # Load environment variables from .env file


# Initialize SQLAlchemy and Bcrypt
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'  # Use SQLite for simplicity
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)

# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

# Registration form
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)


@app.route('/')
def index():
    return render_template('home/index.html')

@app.route('/login')
def login():
    user = User(1)
    login_user(user)
    return redirect(url_for('protected'))

@app.route('/protected')
@login_required
def protected():
    return 'Logged in using Steward'

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return 'Logged out.'

@app.route('/home')
def home():
    return render_template('home/home.html')

@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            # Flash a message to tell the user that email already exists
            flash('Email already exists. Please login or use a different email.', 'danger')
        else:
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user = User(username=form.username.data, email=form.email.data, password=hashed_password)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect(url_for('protected'))
    return render_template('home/register.html', title='Register', form=form)



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
    with app.app_context():
        db.create_all()
    app.run(debug=True)
