import csv
from datetime import datetime, timedelta
import random
from flask import Flask, jsonify, render_template, request, redirect, url_for, session, flash, make_response
import mysql.connector
from flask_login import LoginManager, login_required, current_user, UserMixin, login_user, logout_user
from mysql.connector import Error
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
import re
import json
import os
from werkzeug.utils import secure_filename
from functools import wraps
from io import BytesIO
from email.mime.text import MIMEText
import string
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from mysql.connector import Error
from google_auth_oauthlib.flow import Flow
from oauthlib.oauth2 import WebApplicationClient
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
import smtplib
from google.auth.transport.requests import Request
import requests
from flask_cors import CORS, cross_origin
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = Flask(__name__)
app.config.from_object('config')
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'literaryhub5@gmail.com'
app.config['MAIL_PASSWORD'] = 'vbih iojp zvxk lnob' 
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_DEFAULT_SENDER'] = ('LitHub', 'literaryhub5@gmail.com')
app.secret_key = 'your_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

mail = Mail(app)
user_credentials = {}
otp_storage = {}
  
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'lithub3'

app.config['SESSION_TYPE'] = 'filesystem'
app.config['GOOGLE_CLIENT_ID'] = '1040777284325-7he6na0flmc7017j1pm0eni0t7cg972i.apps.googleusercontent.com'
app.config['GOOGLE_CLIENT_SECRET'] = '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'
app.config['GOOGLE_DISCOVERY_URL'] = "http://localhost:5000/callback"

UPLOAD_FOLDER = os.path.join(app.static_folder, 'images')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

CORS(app)
app.config['JWT_SECRET_KEY'] = 'your_super_secret_key_here'  # change this in production
jwt = JWTManager(app)


# Define the datetime_format filter
@app.template_filter('datetime_format')
def datetime_format(value, format='%Y-%m-%d %H:%M:%S'):
    if isinstance(value, datetime):
        return value.strftime(format)
    return value  # return the original value if it's not a datetime object

# Add this near the top of your app.py with other imports
@app.template_filter('datetime')
def format_datetime(value):
    if isinstance(value, str):
        value = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
    return value.strftime('%Y-%m-%d %H:%M:%S')

# Add User class that inherits from UserMixin
class User(UserMixin):
    def __init__(self, user_id, name, email, password):
        self.id = user_id  # This is required by Flask-Login
        self.name = name
        self.email = email
        self.password = password
        

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=app.config['MYSQL_HOST'],
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD'],
            database=app.config['MYSQL_DB'],
            autocommit=False 
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None
    
# Generate a random OTP
def generate_otp():
    return str(random.randint(100000, 999999))


@login_manager.user_loader
def load_user(user_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute('SELECT * FROM users WHERE user_id = %s', (user_id,))
        user_data = cursor.fetchone()
        if user_data:
            return User(
                user_id=user_data['user_id'],
                name=user_data['name'],
                email=user_data['email'],
                password=user_data['password']
            )
        return None
    finally:
        cursor.close()
        connection.close()

@app.route('/')
def index():
    user = {
        'name': None,
        'email': None,
        'profile_picture': 'default.jpg'  # Set default image initially
    }

    if current_user.is_authenticated:
        user['name'] = current_user.name
        user['email'] = current_user.email
        
        # Get additional user details from database
        connection = get_db_connection()
        if not connection:
            flash('Database connection error. Please try again later.', 'error')
            return render_template('home.html', 
                                user=user,
                                recommended_products=[],
                                popular_products=[],
                                new_products=[],
                                deal_products=[])
        
        cursor = None
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute('SELECT profile_picture FROM users WHERE user_id = %s', (current_user.id,))
            user_data = cursor.fetchone()
            
            if user_data and user_data.get('profile_picture'):
                user['profile_picture'] = user_data['profile_picture']
            else:
                print("No profile picture found, using default.")

        except Exception as e:
            print(f"Error fetching user details: {e}")
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    connection = get_db_connection()
    if not connection:
        flash('Database connection error. Please try again later.', 'error')
        return render_template('home.html', 
                            user=user,
                            recommended_products=[],
                            popular_products=[],
                            new_products=[],
                            deal_products=[])
    
    cursor = None
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Get recommended books (random selection)
        cursor.execute("""
            SELECT 
                p.product_id, 
                p.name, 
                p.price, 
                p.original_price, 
                p.discount_percentage, 
                p.image, 
                p.description, 
                p.author, 
                p.genre,
                COALESCE(
                    ROUND(
                        AVG(NULLIF((r.product_quality + r.seller_service + r.delivery_service) / 3, 0))
                    , 1)
                , 0) as avg_rating
            FROM products p
            LEFT JOIN reviews r ON p.product_id = r.product_id
            GROUP BY 
                p.product_id, 
                p.name, 
                p.price, 
                p.original_price, 
                p.discount_percentage, 
                p.image, 
                p.description, 
                p.author, 
                p.genre
            ORDER BY RAND()
            LIMIT 7
        """)
        recommended_products = cursor.fetchall()
        
        # Get popular books (based on sales)
        cursor.execute("""
            SELECT 
                p.product_id, 
                p.name, 
                p.price, 
                p.original_price, 
                p.discount_percentage,
                p.image, 
                p.description, 
                p.author, 
                p.genre, 
                COUNT(o.order_id) as sales_count
            FROM products p
            LEFT JOIN order_items o ON p.product_id = o.product_id
            GROUP BY 
                p.product_id,
                p.name,
                p.price,
                p.original_price,
                p.discount_percentage,
                p.image,
                p.description,
                p.author,
                p.genre
            ORDER BY sales_count DESC
            LIMIT 4
        """)
        popular_products = cursor.fetchall()
        
        # Get new arrivals
        cursor.execute("""
            SELECT 
                product_id,
                name,
                price,
                original_price,
                discount_percentage,
                image,
                description,
                author,
                genre
            FROM products 
            ORDER BY created_at DESC 
            LIMIT 4
        """)
        new_products = cursor.fetchall()
        
        # Get deals (highest discount)
        cursor.execute("""
            SELECT 
                product_id,
                name,
                price,
                original_price,
                discount_percentage,
                image,
                description,
                author,
                genre
            FROM products
            WHERE discount_percentage > 0
            ORDER BY discount_percentage DESC
            LIMIT 4
        """)
        deal_products = cursor.fetchall()
        
        return render_template('home.html', 
                             user=user,
                             recommended_products=recommended_products,
                             popular_products=popular_products,
                             new_products=new_products,
                             deal_products=deal_products)
    except Exception as e:
        print(f"Error fetching products: {e}")
        return render_template('home.html',
                             user=user,
                             recommended_products=[],
                             popular_products=[],
                             new_products=[],
                             deal_products=[])
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

@app.route('/home')
def home():
    user = None
    if current_user.is_authenticated:
        user = {
            'name': current_user.name,
            'email': current_user.email
        }
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Get recommended books (random selection)
        cursor.execute("""
            SELECT 
                p.product_id, 
                p.name, 
                p.price, 
                p.original_price, 
                p.discount_percentage, 
                p.image, 
                p.description, 
                p.author, 
                p.genre,
                COALESCE(
                    ROUND(
                        AVG(NULLIF((r.product_quality + r.seller_service + r.delivery_service) / 3, 0))
                    , 1)
                , 0) as avg_rating
            FROM products p
            LEFT JOIN reviews r ON p.product_id = r.product_id
            GROUP BY 
                p.product_id, 
                p.name, 
                p.price, 
                p.original_price, 
                p.discount_percentage, 
                p.image, 
                p.description, 
                p.author, 
                p.genre
            ORDER BY RAND()
            LIMIT 7
        """)
        recommended_products = cursor.fetchall()
        
        # Get popular books (based on sales)
        cursor.execute("""
            SELECT 
                p.product_id, 
                p.name, 
                p.price, 
                p.original_price, 
                p.discount_percentage,
                p.image, 
                p.description, 
                p.author, 
                p.genre, 
                COUNT(o.order_id) as sales_count
            FROM products p
            LEFT JOIN order_items o ON p.product_id = o.product_id
            GROUP BY 
                p.product_id,
                p.name,
                p.price,
                p.original_price,
                p.discount_percentage,
                p.image,
                p.description,
                p.author,
                p.genre
            ORDER BY sales_count DESC
            LIMIT 4
        """)
        popular_products = cursor.fetchall()
        
        # Get new arrivals
        cursor.execute("""
            SELECT 
                product_id,
                name,
                price,
                original_price,
                discount_percentage,
                image,
                description,
                author,
                genre
            FROM products 
            ORDER BY created_at DESC 
            LIMIT 4
        """)
        new_products = cursor.fetchall()
        
        # Get deals (highest discount)
        cursor.execute("""
            SELECT 
                product_id,
                name,
                price,
                original_price,
                discount_percentage,
                image,
                description,
                author,
                genre
            FROM products
            WHERE discount_percentage > 0
            ORDER BY discount_percentage DESC
            LIMIT 4
        """)
        deal_products = cursor.fetchall()
        
        return render_template('home.html', 
                             user=user,
                             recommended_products=recommended_products,
                             popular_products=popular_products,
                             new_products=new_products,
                             deal_products=deal_products)
    except Exception as e:
        print(f"Error fetching products: {e}")
        return render_template('home.html',
                             user=user,
                             recommended_products=[],
                             popular_products=[],
                             new_products=[],
                             deal_products=[])
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

def generate_otp():
    return str(random.randint(100000, 999999))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        try:
            first_name = request.form.get('first_name')
            last_name = request.form.get('last_name')
            email = request.form.get('email')
            password = request.form.get('pswd')
            confirm_password = request.form.get('confirm_password')
            
            if not all([first_name, last_name, email, password, confirm_password]):
                flash('All fields are required', 'error')
                return redirect(url_for('login'))
            
            if password != confirm_password:
                flash('Passwords do not match', 'error')
                return redirect(url_for('login'))
            
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)
            
            # Check if email exists
            cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
            if cursor.fetchone():
                flash('Email already registered', 'error')
                return redirect(url_for('login'))
            
            # Generate verification code
            verification_code = ''.join(random.choices('0123456789', k=6))
            
            # Store in session
            session['temp_user'] = {
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'password': generate_password_hash(password),
                'verification_code': verification_code
            }
            
            # Flash the verification code
            flash(f'Your verification code is: {verification_code}', 'success')
            
            # Important: Return the template directly instead of redirecting
            return render_template('loginuser.html')
            
        except Exception as e:
            print(f"Error in signup: {str(e)}")
            flash('An error occurred during signup', 'error')
            return redirect(url_for('login'))
            
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'connection' in locals():
                connection.close()
                
@app.route('/verify_email', methods=['GET', 'POST'])
def verify_email():
    if 'temp_user' not in session:
        flash('Please sign up first', 'error')
        return redirect(url_for('signup'))
        
    if request.method == 'POST':
        verification_code = request.form.get('verification_code')
        temp_user = session['temp_user']
        
        if verification_code == temp_user['verification_code']:
            try:
                connection = get_db_connection()
                cursor = connection.cursor()
                
                # Insert verified user into database
                cursor.execute('''
                    INSERT INTO users (name, email, password, is_verified) 
                    VALUES (%s, %s, %s, TRUE)
                ''', (f"{temp_user['first_name']} {temp_user['last_name']}", temp_user['email'], temp_user['password']))
                
                connection.commit()
                
                # Clear temporary user data
                session.pop('temp_user', None)
                
                flash('Account verified successfully! Please login.', 'success')
                return redirect(url_for('login'))
                
            except Exception as e:
                print(f"Error in email verification: {str(e)}")
                flash('An error occurred during verification', 'error')
                
            finally:
                if cursor:
                    cursor.close()
                if connection:
                    connection.close()
        else:
            flash('Invalid verification code', 'error')
            
    return render_template('verify_email.html')

@app.route('/otp_modal', methods=['GET', 'POST'])
def otp_modal():
    email = session.get('email')
    
    if not email:
        flash('Please complete the signup process first.', 'warning')
        return redirect(url_for('signup'))

    if request.method == 'POST':
        entered_otp = request.form.get('otp')

        if entered_otp == otp_storage.get(email):
            try:
                connection = get_db_connection()
                cursor = connection.cursor(dictionary=True)
                
                # Get user information
                cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
                user = cursor.fetchone()
                
                if user:
                    # Set all session variables for login
                    session['loggedin'] = True
                    session['id'] = user['user_id']
                    session['name'] = user['name']
                    session['email'] = user['email']
                    
                    # Clear temporary storage
                    otp_storage.pop(email, None)
                    
                    flash('Account verified successfully! You are now logged in.', 'success')
                    return redirect(url_for('index'))
                
            except Exception as e:
                flash(f'Error during verification: {str(e)}', 'danger')
                return redirect(url_for('signup'))
            finally:
                cursor.close()
                connection.close()
        else:
            flash('Invalid OTP. Please try again.', 'danger')
            return render_template('otpmodal.html', email=email)

    return render_template('otpmodal.html', email=email)

@app.route('/verify-otp-login', methods=['POST'])
def verify_otp_login():
    try:
        entered_otp = request.form.get('otp')
        temp_user = session.get('temp_user')
        
        if not temp_user:
            flash('Session expired. Please sign up again.', 'error')
            return redirect(url_for('login'))
            
        if entered_otp == temp_user['verification_code']:
            connection = get_db_connection()
            cursor = connection.cursor()
            
            # Insert user into database without is_verified column

            cursor.execute('''
                INSERT INTO users (name, email, password, is_verified) 
                VALUES (%s, %s, %s, TRUE)
            ''', (f"{temp_user['first_name']} {temp_user['last_name']}", temp_user['email'], temp_user['password']))
                        
            connection.commit()
            
            # Clear session
            session.pop('temp_user', None)
            
            flash('Account created successfully! Please login.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Invalid OTP. Please try again.', 'error')
            return render_template('loginuser.html', show_verify_modal=True)
            
    except Exception as e:
        print(f"Error in OTP verification: {str(e)}")
        flash('An error occurred during verification', 'error')
        return redirect(url_for('login'))
        
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()
    
@app.route("/success")
def success():
    return "<h1>Welcome! You have successfully signed up and logged in.</h1>"

def generate_captcha():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

@app.route('/google_login')
def google_login():
    try:
        # Store current user info if logged in
        current_user_data = None
        if 'loggedin' in session:
            current_user_data = {
                'id': session.get('id'),
                'email': session.get('email'),
                'name': session.get('name')
            }
        
        # Clear session but keep user data
        session.clear()
        
        # Create flow instance
        flow = Flow.from_client_secrets_file(
            'client_secret.json',
            scopes=[
                'openid',
                'https://www.googleapis.com/auth/userinfo.email',
                'https://www.googleapis.com/auth/userinfo.profile'
            ],
            redirect_uri='http://localhost:5000/callback'
        )
        
        # Generate authorization URL and state
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )
        
        # Store state and user data in session
        session.permanent = True
        session['google_state'] = state
        if current_user_data:
            session['previous_user'] = current_user_data
        
        print(f"Google Login - Generated state: {state}")
        print(f"Google Login - Session data: {dict(session)}")
        
        # Force session to be saved
        session.modified = True
        
        return redirect(authorization_url)
        
    except Exception as e:
        print(f"Error in google_login: {str(e)}")
        flash('Failed to initialize Google login', 'error')
        return redirect(url_for('login'))

@app.route('/callback')
def callback():
    try:
        state = request.args.get('state')
        stored_state = session.get('google_state')
        
        print(f"Callback - Received state: {state}")
        print(f"Callback - Stored state: {stored_state}")
        print(f"Callback - Current session: {dict(session)}")
        
        if not state or not stored_state or state != stored_state:
            print("State verification failed")
            previous_user = session.get('previous_user')
            session.clear()
            
            # Restore previous user session if exists
            if previous_user:
                session.update({
                    'loggedin': True,
                    'id': previous_user['id'],
                    'email': previous_user['email'],
                    'name': previous_user['name']
                })
            
            flash('Authentication failed. Please try again.', 'error')
            return redirect(url_for('login'))

        # Create flow instance
        flow = Flow.from_client_secrets_file(
            'client_secret.json',
            scopes=[
                'openid',
                'https://www.googleapis.com/auth/userinfo.email',
                'https://www.googleapis.com/auth/userinfo.profile'
            ],
            redirect_uri='http://localhost:5000/callback',
            state=state
        )
        
        # Get the authorization code
        flow.fetch_token(authorization_response=request.url)
        
        # Get user info
        credentials = flow.credentials
        userinfo_endpoint = "https://www.googleapis.com/oauth2/v3/userinfo"
        headers = {'Authorization': f'Bearer {credentials.token}'}
        userinfo_response = requests.get(userinfo_endpoint, headers=headers)
        userinfo_response.raise_for_status()
        user_info = userinfo_response.json()
        
        email = user_info.get('email')
        name = user_info.get('name')
        
        if not email or not name:
            raise ValueError("Failed to get email or name from Google response")
        
        # Database operations
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        try:
            cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
            user = cursor.fetchone()
            
            if not user:
                cursor.execute('''
                    INSERT INTO users (name, email, password, is_google_user, status)
                    VALUES (%s, %s, %s, TRUE, 'active')
                ''', (name, email, 'google_user'))
                connection.commit()
                user_id = cursor.lastrowid
            else:
                user_id = user['user_id']
            
            # Set new session data
            session.clear()
            session.permanent = True
            session['loggedin'] = True
            session['id'] = user_id
            session['name'] = name
            session['email'] = email
            session['is_google_user'] = True
            
            # Force session to be saved
            session.modified = True
            
            print(f"New session after Google login: {dict(session)}")
            
        finally:
            cursor.close()
            connection.close()
        
        flash('Successfully logged in with Google!', 'success')
        return redirect(url_for('index'))
        
    except Exception as e:
        print(f"Error in callback: {str(e)}")
        session.clear()
        flash('Failed to complete Google authentication', 'error')
        return redirect(url_for('login'))


# Update the Google OAuth2 configuration constants
GOOGLE_CLIENT_ID = '1040777284325-7he6na0flmc7017j1pm0eni0t7cg972i.apps.googleusercontent.com'
GOOGLE_CLIENT_SECRET = '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'
REDIRECT_URI = 'http://localhost:5000/callback'
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"
SCOPES = [
    'openid',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile'
]

# Initialize OAuth 2 client
client = WebApplicationClient(GOOGLE_CLIENT_ID)

# Route for login
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Create a dictionary for template arguments that will always include the site key
    template_args = {'recaptcha_site_key': app.config['RECAPTCHA_SITE_KEY']}

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['pswd']
        recaptcha_response = request.form.get('g-recaptcha-response')

        # Verify reCAPTCHA first
        if not recaptcha_response:
            flash('Please complete the reCAPTCHA.', 'error')
            return render_template('loginuser.html', **template_args)

        # Verify with Google
        verify_response = requests.post('https://www.google.com/recaptcha/api/siteverify', {
            'secret': app.config['RECAPTCHA_SECRET_KEY'],
            'response': recaptcha_response
        }).json()

        if not verify_response['success']:
            flash('Invalid reCAPTCHA. Please try again.', 'error')
            return render_template('loginuser.html', **template_args)

        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        account = cursor.fetchone()

        if account and check_password_hash(account[3], password):
            user = User(account[0], account[1], account[2], account[3])
            login_user(user)
            session['loggedin'] = True
            session['id'] = account[0]
            session['name'] = account[1]
            session['email'] = account[2]
            session['password'] = account[3]
            flash('You have successfully logged in!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Incorrect email or password. Please try again.', 'error')
            return render_template('loginuser.html', **template_args)

        cursor.close()
        connection.close()

    # For GET requests
    return render_template('loginuser.html', **template_args)
    
@app.route('/profile')
def profile():
    user_id = session.get('id')
    status = request.args.get('status')  # Get status from query parameter
    
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    # Fetch user information
    cursor.execute('SELECT * FROM users WHERE user_id = %s', (user_id,))
    user = cursor.fetchone()
    
    # Build the query based on status filter
    query = '''
        SELECT o.order_id, o.order_date, o.total_price, o.status, 
               oi.quantity, oi.price as item_price, p.name as product_name, 
               p.image,
               p.product_id,
               o.shipping_address
        FROM orders o
        JOIN order_items oi ON o.order_id = oi.order_id
        JOIN products p ON oi.product_id = p.product_id
        WHERE o.buyer_id = %s
    '''
    
    params = [user_id]
    if status:
        query += ' AND o.status = %s'
        params.append(status)
    
    query += ' ORDER BY o.order_date DESC'
    
    cursor.execute(query, tuple(params))
    orders_data = cursor.fetchall()
    
    # Group items by order ID
    orders_list = []
    current_order = None
    
    for order in orders_data:
        if not current_order or current_order['order_id'] != order['order_id']:
            if current_order:
                orders_list.append(current_order)
            current_order = {
                'order_id': order['order_id'],
                'order_date': order['order_date'],
                'total_price': order['total_price'],
                'status': order['status'],
                'shipping_address': order['shipping_address'],
                'order_items': []  # Renamed to avoid conflicts
            }
        
        current_order['order_items'].append({
            'name': order['product_name'],
            'quantity': order['quantity'],
            'price': order['item_price'],
            'image': order['image'],
            'product_id': order['product_id']
        })
    
    if current_order:
        orders_list.append(current_order)

    cursor.close()
    connection.close()
    
    return render_template('user-purchase-history.html', user=user, orders=orders_list, status=status)



def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/user_profile')
def user_profile():
    if 'loggedin' not in session:
        flash('Please log in to view your profile.', 'error')
        return redirect(url_for('login'))
    
    user_id = session.get('id')
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        # Join users and user_details tables
        cursor.execute(''' 
            SELECT u.*, ud.* 
            FROM users u 
            LEFT JOIN user_details ud ON u.user_id = ud.user_id 
            WHERE u.user_id = %s
        ''', (user_id,))
        
        user = cursor.fetchall()  # Fetch all results, could be a list even if only one user is expected.

        # Ensure user is not None before template rendering
        if not user:
            user = {}  # Provide empty dict if no user found
        else:
            user = user[0]  # If there are results, take the first one

    except mysql.connector.Error as err:
        flash(f'Error fetching user data: {err}', 'error')
        user = {}  # Set user to empty dict on error

    finally:
        cursor.close()  # Close cursor
        connection.close()  # Close connection

    return render_template('user-profile.html', user=user)


@app.route('/update_profile', methods=['POST'])
def update_profile():
    if 'loggedin' not in session:
        flash('Please log in to update your profile.', 'error')
        return redirect(url_for('login'))

    # Retrieve data from form
    user_id = session.get('id')
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    gender = request.form.get('gender')
    date_of_birth = request.form.get('date_of_birth')

    connection = get_db_connection()

    try:
        with connection.cursor(dictionary=True) as cursor:
            # Update `users` table
            cursor.execute('''
                UPDATE users 
                SET name = %s, email = %s, gender = %s, date_of_birth = %s
                WHERE user_id = %s
            ''', (name, email, gender, date_of_birth, user_id))
            
            # Check if user details exist
            cursor.execute('SELECT * FROM user_details WHERE user_id = %s', (user_id,))
            user_details = cursor.fetchone()

            if user_details:
                cursor.execute('''
                    UPDATE user_details 
                    SET phone = %s
                    WHERE user_id = %s
                ''', (phone, user_id))
            else:
                cursor.execute('''
                    INSERT INTO user_details (user_id, phone)
                    VALUES (%s, %s)
                ''', (user_id, phone))

        # Commit the transaction after all queries are executed
        connection.commit()
        flash('Profile updated successfully!', 'success')

    except mysql.connector.Error as err:
        connection.rollback()
        flash(f'Error updating profile: {str(err)}', 'error')
    finally:
        connection.close()

    return redirect(url_for('user_profile'))

@app.route('/update_profile_picture', methods=['POST'])
def update_profile_picture():
    # Check if user is logged in
    if 'loggedin' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'}), 401
        
    try:
        if 'profile_picture' not in request.files:
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        file = request.files['profile_picture']
        
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            # Create secure filename with timestamp
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
            filename = timestamp + filename
            
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)
            
            try:
                # Save the file
                file_path = os.path.join('static', 'images', 'profile', filename)
                file.save(file_path)
                
                # Update database with user ID from session
                user_id = session['id']  # Get user ID from session
                cursor.execute("UPDATE users SET profile_picture = %s WHERE user_id = %s", 
                             (filename, user_id))  # Changed 'id' to 'user_id'
                connection.commit()
                
                cursor.close()
                connection.close()
                
                return jsonify({
                    'success': True,
                    'message': 'Profile picture updated successfully',
                    'filename': filename
                })
                
            except Exception as e:
                if os.path.exists(file_path):
                    os.remove(file_path)
                return jsonify({'success': False, 'error': str(e)}), 500
                
        return jsonify({'success': False, 'error': 'Invalid file type'}), 400
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/user_purchase')
def user_purchase():
    user_id = session.get('id')
    status = request.args.get('status')  # Get status from query parameter
    
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    # Fetch user information
    cursor.execute('SELECT * FROM users WHERE user_id = %s', (user_id,))
    user = cursor.fetchone()
    
    # Build the query based on status filter
    query = '''
        SELECT o.order_id, o.order_date, o.total_price, o.status, 
               oi.quantity, oi.price as item_price, p.name as product_name, 
               p.image,
               p.product_id,
               o.shipping_address
        FROM orders o
        JOIN order_items oi ON o.order_id = oi.order_id
        JOIN products p ON oi.product_id = p.product_id
        WHERE o.buyer_id = %s
    '''
    
    params = [user_id]
    if status:
        query += ' AND o.status = %s'
        params.append(status)
    
    query += ' ORDER BY o.order_date DESC'
    
    cursor.execute(query, tuple(params))
    orders_data = cursor.fetchall()
    
    # Group items by order ID
    orders_list = []
    current_order = None
    
    for order in orders_data:
        if not current_order or current_order['order_id'] != order['order_id']:
            if current_order:
                orders_list.append(current_order)
            current_order = {
                'order_id': order['order_id'],
                'order_date': order['order_date'],
                'total_price': order['total_price'],
                'status': order['status'],
                'shipping_address': order['shipping_address'],
                'order_items': []  # Renamed to avoid conflicts
            }
        
        current_order['order_items'].append({
            'name': order['product_name'],
            'quantity': order['quantity'],
            'price': order['item_price'],
            'image': order['image'],
            'product_id': order['product_id']
        })
    
    if current_order:
        orders_list.append(current_order)

    cursor.close()
    connection.close()
    
    return render_template('user-purchase-history.html', user=user, orders=orders_list, status=status)


@app.route('/user_password')
def user_password():
    user_id = session.get('id')
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    cursor.execute('SELECT * FROM users WHERE user_id = %s', (user_id,))
    user = cursor.fetchone()
    
    cursor.close()
    connection.close()

    # Render the change password section as a standalone page
    return render_template('user-change-pass.html', user=user)

@app.route('/change_password', methods=['POST'])
def change_password():
    if 'loggedin' not in session:
        return jsonify({'error': 'Please log in to change password'}), 401

    try:
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        print(f"Received passwords: current={bool(current_password)}, new={bool(new_password)}, confirm={bool(confirm_password)}")
        
        if not all([current_password, new_password, confirm_password]):
            return jsonify({'error': 'All fields are required'}), 400
            
        if new_password != confirm_password:
            return jsonify({'error': 'New passwords do not match'}), 400
            
        user_id = session['id']
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Get current user's password
        cursor.execute("SELECT password FROM users WHERE user_id = %s", (user_id,))
        user = cursor.fetchone()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Debug print the password check
        stored_hash = user['password']
        is_valid = check_password_hash(stored_hash, current_password)
        print(f"Password check: stored={stored_hash}, valid={is_valid}")
        
        # Update password
        new_hash = generate_password_hash(new_password, method='scrypt')
        cursor.execute("UPDATE users SET password = %s WHERE user_id = %s", 
                     (new_hash, user_id))
        connection.commit()
        
        cursor.close()
        connection.close()
        
        return jsonify({
            'success': True,
            'message': 'Password updated successfully!'
        })
        
    except Exception as e:
        print(f"Error in change_password: {str(e)}")  # Debug print
        return jsonify({
            'error': 'An error occurred while changing password',
            'details': str(e)
        }), 500
        
def generate_otp():
    return ''.join(random.choices(string.digits, k=6))  # Simple 6-digit OTP

def send_email(recipient, otp):
    try:
        msg = Message(
            subject='Password Reset OTP',
            recipients=[recipient],
            body=f'Your OTP for password reset is: {otp}',
            sender=app.config['MAIL_DEFAULT_SENDER']
        )
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Email sending error: {e}")
        return False

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        print(f"Email: {email}")
        print(f"Form data: {request.form}")

        try:
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)
            
            # Verify email exists
            cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
            user = cursor.fetchone()

            if not user:
                flash('Email address not found.', 'danger')
                return render_template('forgot-password.html')

            # Generate OTP
            otp = generate_otp()
            print(f"Generated OTP: {otp}")

            # Store only email and OTP in session for now
            session['reset_data'] = {
                'email': email,
                'otp': otp
            }

            # Send OTP email
            try:
                msg = Message(
                    'Password Reset OTP',
                    sender=app.config['MAIL_DEFAULT_SENDER'],
                    recipients=[email]
                )
                msg.body = f'Your OTP for password reset is: {otp}'
                mail.send(msg)
                
                flash('OTP has been sent to your email.', 'success')
                return render_template('otpmodal.html', email=email)
                
            except Exception as e:
                print(f"Email error: {str(e)}")
                flash('Error sending OTP email. Please try again.', 'danger')
                return render_template('forgot-password.html')

        except Exception as e:
            print(f"General error: {str(e)}")
            flash('An error occurred. Please try again.', 'danger')
            return render_template('forgot-password.html')
            
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'connection' in locals():
                connection.close()

    # GET request
    return render_template('forgot-password.html')

@app.route('/verify_reset_otp', methods=['POST'])
def verify_reset_otp():
    if 'reset_data' not in session:
        flash('Password reset session expired. Please try again.', 'danger')
        return redirect(url_for('forgot_password'))

    entered_otp = request.form.get('otp')
    reset_data = session['reset_data']

    if entered_otp != reset_data['otp']:
        flash('Invalid OTP. Please try again.', 'danger')
        return render_template('otpmodal.html', email=reset_data['email'])

    # If OTP is valid, show password reset form
    return render_template('reset_password.html', email=reset_data['email'])

@app.route('/reset_password', methods=['POST'])
def reset_password():
    if 'reset_data' not in session:
        flash('Password reset session expired. Please try again.', 'danger')
        return redirect(url_for('forgot_password'))

    email = session['reset_data']['email']
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')

    if not new_password or not confirm_password:
        flash('Please enter both passwords.', 'danger')
        return render_template('reset_password.html', email=email)

    if new_password != confirm_password:
        flash('Passwords do not match.', 'danger')
        return render_template('reset_password.html', email=email)

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Hash the new password
        hashed_password = generate_password_hash(new_password)

        # Update password
        cursor.execute(
            'UPDATE users SET password = %s WHERE email = %s',
            (hashed_password, email)
        )
        connection.commit()

        # Clear session
        session.pop('reset_data', None)

        flash('Password has been reset successfully! Please login with your new password.', 'success')
        return redirect(url_for('login'))

    except Exception as e:
        print(f"Password update error: {str(e)}")
        flash('Error updating password. Please try again.', 'danger')
        return render_template('reset_password.html', email=email)

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

@app.route('/user_bank')
def user_bank():
    if 'loggedin' not in session:
        flash('Please log in to view your bank details', 'error')
        return redirect(url_for('login'))
    
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        # First get user data
        cursor.execute('SELECT * FROM users WHERE user_id = %s', (session['id'],))
        user = cursor.fetchone()  # Get user as dictionary
        
        if not user:
            flash('User not found', 'error')
            return redirect(url_for('home'))
            
        # Then get payment methods
        cursor.execute('SELECT * FROM payment_methods WHERE user_id = %s', (session['id'],))
        payment_methods = cursor.fetchall()  # Get all payment methods
        
        return render_template('user-bank.html', 
                             user=user,  # Pass user data for profile display
                             payment_methods=payment_methods)  # Pass payment methods separately
                             
    except mysql.connector.Error as e:
        print(f"Database error: {e}")
        flash('Database error occurred', 'error')
        return redirect(url_for('home'))
        
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route('/add_card', methods=['POST'])
def add_card():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Extract card details
        card_number = request.form.get('card_number')
        card_name = request.form.get('card_name')
        expiry = request.form.get('expiry').split('/')
        exp_month = expiry[0]
        exp_year = expiry[1]
        
        # Store only last 4 digits of card number
        last_four = card_number[-4:]
        
        cursor.execute('''
            INSERT INTO payment_methods 
            (user_id, card_name, last_four, exp_month, exp_year)
            VALUES (%s, %s, %s, %s, %s)
        ''', (session['id'], card_name, last_four, exp_month, exp_year))
        
        connection.commit()
        flash('Card added successfully', 'success')
        
    except Exception as e:
        flash('Error adding card: ' + str(e), 'error')
    finally:
        cursor.close()
        connection.close()
    
    return redirect(url_for('user_bank'))

@app.route('/delete_bank/<int:bank_id>')
def delete_bank(bank_id):
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    cursor = mysql.connection.cursor()
    cursor.execute('DELETE FROM bank_details WHERE id = %s AND user_id = %s', 
                  (bank_id, session['id']))
    mysql.connection.commit()
    cursor.close()
    
    return redirect(url_for('user_bank'))


@app.route('/user_seller_reg')
def user_seller_reg():
    if 'loggedin' not in session:
        flash('Please log in first', 'error')
        return redirect(url_for('login'))

    user_id = session.get('id')
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    # Fetch user data
    cursor.execute('SELECT * FROM users WHERE user_id = %s', (user_id,))
    user = cursor.fetchone()
    
    # Check for pending seller request
    cursor.execute('''
        SELECT * FROM seller_requests 
        WHERE user_id = %s AND status = 'pending'
        ORDER BY request_date DESC LIMIT 1
    ''', (user_id,))
    pending_request = cursor.fetchone()
    
    cursor.close()
    connection.close()

    return render_template('user-seller-registration.html', 
                         user=user, 
                         pending_request=pending_request)

@app.route('/seller_registration', methods=['POST'])
def seller_registration():
    if 'loggedin' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Check if already registered as seller
        cursor.execute('SELECT is_seller FROM users WHERE user_id = %s', (session['id'],))
        user = cursor.fetchone()
        
        if user['is_seller']:
            return jsonify({'error': 'Already registered as seller'}), 400
        
        # Check for existing pending request
        cursor.execute('''
            SELECT * FROM seller_requests 
            WHERE user_id = %s AND status = 'pending'
        ''', (session['id'],))
        
        if cursor.fetchone():
            return jsonify({'error': 'You already have a pending registration request'}), 400
        
        # Insert seller registration request
        cursor.execute('''
            INSERT INTO seller_requests (user_id, status, request_date)
            VALUES (%s, 'pending', CURRENT_TIMESTAMP)
        ''', (session['id'],))
        
        connection.commit()
        return jsonify({'message': 'Seller registration request submitted successfully'})
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        connection.close()

def get_user_notifications(user_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Query to get all notifications for the user
        cursor.execute('''
            SELECT 
                notification_id,
                message,
                type,
                order_id,
                created_at,
                is_read
            FROM notifications 
            WHERE user_id = %s 
            ORDER BY created_at DESC
        ''', (user_id,))
        
        notifications = cursor.fetchall()
        return notifications
        
    except Exception as e:
        print(f"Error getting notifications: {str(e)}")
        return []
        
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route('/user_notif')
def user_notif():
    if 'id' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('login'))
        
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Get user info
        cursor.execute('SELECT * FROM users WHERE user_id = %s', (session['id'],))
        user = cursor.fetchone()
        
        # Get notifications
        cursor.execute('''
            SELECT 
                notification_id,
                message,
                type,
                order_id,
                created_at,
                is_read
            FROM notifications 
            WHERE user_id = %s 
            ORDER BY created_at DESC
        ''', (session['id'],))
        
        notifications = cursor.fetchall()
        
        print(f"Found {len(notifications)} notifications for user {session['id']}")
        for notif in notifications:
            print(f"Notification: {notif}")
        
        return render_template('user-notif.html', 
                             user=user,
                             notifications=notifications)
                             
    except Exception as e:
        print(f"Error in user_notif: {str(e)}")
        flash('An error occurred while fetching notifications', 'error')
        return redirect(url_for('home'))
        
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


@app.route('/mark_notification_read', methods=['POST'])
def mark_notification_read():
    if 'id' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'})
        
    try:
        data = request.get_json()
        notification_id = data.get('notification_id')
        
        if not notification_id:
            return jsonify({'success': False, 'error': 'No notification ID provided'})
            
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Verify the notification belongs to the user
        cursor.execute('''
            UPDATE notifications 
            SET is_read = 1 
            WHERE notification_id = %s AND user_id = %s
        ''', (notification_id, session['id']))
        
        connection.commit()
        return jsonify({'success': True})
        
    except Exception as e:
        print(f"Error marking notification as read: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})
        
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route('/approve_seller/<int:request_id>', methods=['POST'])
def approve_seller(request_id):
    if 'loggedin' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Unauthorized'}), 403
        
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Get the user_id from seller_requests
        cursor.execute('SELECT user_id FROM seller_requests WHERE request_id = %s', (request_id,))
        seller_request = cursor.fetchone()
        
        if not seller_request:
            return jsonify({'error': 'Seller request not found'}), 404
            
        # Update user to seller status
        cursor.execute('UPDATE users SET is_seller = TRUE WHERE user_id = %s', (seller_request['user_id'],))
        
        # Update request status
        cursor.execute('UPDATE seller_requests SET status = "approved" WHERE request_id = %s', (request_id,))
        
        # Add notification instead of sending email
        cursor.execute('''
            INSERT INTO notifications 
            (user_id, message, type, created_at) 
            VALUES (%s, "Your seller registration has been approved! You can now start selling.", "seller_approval", CURRENT_TIMESTAMP)
        ''', (seller_request['user_id'],))
        
        connection.commit()
        return jsonify({'message': 'Seller approved successfully'})
        
    except Error as e:
        print(f"Error in approve_seller: {str(e)}")
        return jsonify({'error': str(e)}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

# Helper functions 
def verify_password(plain_password, hashed_password):
    # Implement your password verification logic here
    pass

def hash_password(password):
    # Implement your password hashing logic here
    pass


@app.route('/user_address')
def user_address():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    # Fetch all addresses for the logged-in user
    cursor.execute(''' 
        SELECT * FROM user_details 
        WHERE user_id = %s 
        ORDER BY is_default DESC
    ''', (session['id'],))
    
    addresses = cursor.fetchall()
    
    
    cursor.execute(''' 
        SELECT * FROM users 
        WHERE user_id = %s 
    ''', (session['id'],))  
    user = cursor.fetchone()  

    cursor.close()
    connection.close()
    
    return render_template('user-address.html', addresses=addresses, user=user)


@app.route('/get_address/<int:address_id>')
def get_address(address_id):
    if 'loggedin' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    cursor.execute('''
        SELECT * FROM user_details 
        WHERE id = %s AND user_id = %s
    ''', (address_id, session['id']))
    
    address = cursor.fetchone()
    
    cursor.close()
    connection.close()
    
    if address:
        return jsonify(address)
    return jsonify({'error': 'Address not found'}), 404

@app.route('/add_address', methods=['POST'])
def add_address():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Check if this is the first address
        cursor.execute('SELECT COUNT(*) FROM user_details WHERE user_id = %s', (session['id'],))
        is_first_address = cursor.fetchone()[0] == 0
        
        # Insert new address
        cursor.execute('''
            INSERT INTO user_details 
            (user_id, first_name, last_name, phone, address, city, 
             province, country, postcode, barangay, email, is_default)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                (SELECT IF(COUNT(*) = 0, 1, 0) FROM 
                    (SELECT 1 FROM user_details WHERE user_id = %s) as tmp))
        ''', (
            session['id'],
            request.form['first_name'],
            request.form['last_name'],
            request.form['phone'],
            request.form['address'],
            request.form['city'],
            request.form['province'],
            request.form.get('country', 'Philippines'),
            request.form['postcode'],
            request.form['barangay'],
            request.form['email'],
            session['id']
        ))
        
        connection.commit()
        flash('Address added successfully!', 'success')
    except Exception as e:
        connection.rollback()
        flash(f'Error adding address: {str(e)}', 'error')
    finally:
        cursor.close()
        connection.close()
    
    return redirect(url_for('user_address'))

@app.route('/edit_address', methods=['POST'])
def edit_address():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    connection = get_db_connection()
    cursor = connection.cursor()
    
    try:
        # Update address
        cursor.execute('''
            UPDATE user_details 
            SET first_name = %s, last_name = %s, address = %s, 
                city = %s, province = %s, country = %s, 
                postcode = %s, phone = %s, barangay = %s, email = %s
            WHERE id = %s AND user_id = %s
        ''', (
            request.form['first_name'],
            request.form['last_name'],
            request.form['address'],
            request.form['city'],
            request.form['province'],
            request.form.get('country', 'Philippines'),
            request.form['postcode'],
            request.form['phone'],
            request.form['barangay'],
            request.form['email'],
            request.form['address_id'],
            session['id']
        ))
        
        connection.commit()
        flash('Address updated successfully!', 'success')
    except Exception as e:
        connection.rollback()
        flash(f'Error updating address: {str(e)}', 'error')
    finally:
        cursor.close()
        connection.close()
    
    return redirect(url_for('user_address'))
@app.route('/delete_address/<int:address_id>')
def delete_address(address_id):
    if 'loggedin' not in session:
        flash('Please log in to delete an address.', 'error')
        return redirect(url_for('login'))
    
    connection = get_db_connection()
    cursor = connection.cursor()
    
    try:
        # Debug: Log the user ID and address ID being used
        print(f"Attempting to delete address with ID: {address_id} for user ID: {session['id']}")

        # Delete address
        cursor.execute('DELETE FROM user_details WHERE user_id = %s AND id = %s', 
                      (session['id'], address_id))
        
        # Check if any rows were affected
        if cursor.rowcount > 0:
            print(f"Successfully deleted address ID: {address_id}")
            # If deleted address was default, set a new default
            cursor.execute(''' 
                UPDATE user_details 
                SET is_default = TRUE 
                WHERE user_id = %s 
                ORDER BY id LIMIT 1
            ''', (session['id'],))
            connection.commit()
            flash('Address deleted successfully!', 'success')
        else:
            print(f"No address found with ID: {address_id} for user ID: {session['id']}")
            flash('No address found to delete.', 'warning')
        
    except Exception as e:
        connection.rollback()
        print(f"Error deleting address: {str(e)}")  # Log the error
        flash(f'Error deleting address: {str(e)}', 'error')
    finally:
        cursor.close()
        connection.close()

    return redirect(url_for('user_address'))

# Route for services
@app.route('/service')
def service():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
        
    # Get user data from database
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        cursor.execute('SELECT * FROM users WHERE user_id = %s', (session['id'],))
        user = cursor.fetchone()
        
        if not user:
            return redirect(url_for('login'))
            
        return render_template('service.html', user=user)
        
    except Exception as e:
        print(f"Error in service route: {str(e)}")
        return redirect(url_for('login'))
        
    finally:
        cursor.close()
        connection.close()


# Route for contact
def get_user_data():
    """Helper function to get user data for templates"""
    if 'loggedin' in session:
        connection = get_db_connection()
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute('SELECT * FROM users WHERE user_id = %s', (session['id'],))
            user = cursor.fetchone()
            cursor.close()
            return user
        except Exception as e:
            print(f"Error fetching user data: {e}")
            return None
        finally:
            connection.close()
    return None

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    # Initialize user data
    user_data = get_user_data() if 'loggedin' in session else None
    
    if request.method == 'POST':
        try:
            # Get form data
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip()
            phone = request.form.get('phone', '').strip()
            message = request.form.get('message', '').strip()
            user_id = session.get('id') if 'loggedin' in session else None

            # Validate required fields
            if not all([name, email, message]):
                flash('Please fill in all required fields (name, email, and message).', 'error')
                return redirect(url_for('contact'))

            connection = get_db_connection()
            try:
                cursor = connection.cursor(dictionary=True)
                
                # First check if the table exists and has the correct structure
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS contact_messages (
                        message_id int(11) NOT NULL AUTO_INCREMENT,
                        user_id int(11) DEFAULT NULL,
                        name varchar(255) NOT NULL,
                        email varchar(255) NOT NULL,
                        phone varchar(20) DEFAULT NULL,
                        message text NOT NULL,
                        status enum('unread','read','replied') DEFAULT 'unread',
                        created_at timestamp NOT NULL DEFAULT current_timestamp(),
                        PRIMARY KEY (message_id)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci
                """)
                connection.commit()

                # Insert the message
                sql = """
                    INSERT INTO contact_messages 
                    (user_id, name, email, phone, message, status) 
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                values = (user_id, name, email, phone, message, 'unread')
                
                print(f"Debug - Values being inserted: {values}")
                cursor.execute(sql, values)
                connection.commit()
                
                print(f"Debug - Message inserted successfully with ID: {cursor.lastrowid}")
                flash('Your message has been sent successfully! We will get back to you soon.', 'success')
                
            except mysql.connector.Error as db_err:
                connection.rollback()
                error_msg = str(db_err)
                print(f"Debug - Database error: {error_msg}")
                # Show the actual error message to help debug
                flash(f'Database error: {error_msg}', 'error')
                
            finally:
                cursor.close()
                connection.close()
                
        except Exception as e:
            print(f"Error in contact form: {e}")
            flash('An unexpected error occurred. Please try again later.', 'error')
        
        return redirect(url_for('contact'))

    # GET request - display the contact form
    return render_template('contact.html', user=user_data)


# Helper function to get a product by ID
def get_product(product_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute('SELECT * FROM products WHERE product_id = %s', (product_id,))
    product = cursor.fetchone()
    cursor.close()
    connection.close()
    return product


# View Cart (persistent for logged-in users)
@app.route('/cart')
def view_cart():
    print("Starting cart view function")  # Debug log 1
    
    # Check if user is logged in
    if not session.get('loggedin'):
        print("No loggedin in session")  # Debug log 2
        flash('Please log in to view your cart.', 'error')
        return redirect(url_for('login'))

    user_id = session.get('id')
    print(f"User ID from session: {user_id}")  # Debug log 3
    
    if not user_id:
        print("No user_id in session")  # Debug log 4
        flash('Session error. Please log in again.', 'error')
        return redirect(url_for('login'))

    try:
        print("Attempting database connection")  # Debug log 5
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Verify user exists
        cursor.execute('SELECT * FROM users WHERE user_id = %s', (user_id,))
        user = cursor.fetchone()
        
        if not user:
            session.clear()
            flash('User account not found. Please log in again.', 'error')
            return redirect(url_for('login'))

        # Get cart items with additional product details
        cursor.execute('''
            SELECT 
                c.cart_id,
                c.quantity,
                p.product_id,
                p.name,
                p.price,
                p.image,
                p.discount_percentage,
                p.quantity as available_quantity,
                (p.price * (1 - p.discount_percentage/100) * c.quantity) as total_price
            FROM cart c
            JOIN products p ON c.product_id = p.product_id
            WHERE c.user_id = %s
        ''', (user_id,))
        
        cart_items = cursor.fetchall()
        
        # Calculate cart total and handle out of stock items
        cart_total = 0
        for item in cart_items:
            # Check if item is out of stock or quantity exceeds available
            if item['available_quantity'] == 0:
                item['status'] = 'out_of_stock'
            elif item['quantity'] > item['available_quantity']:
                item['status'] = 'quantity_exceeded'
                item['quantity'] = item['available_quantity']  # Adjust quantity
            else:
                item['status'] = 'available'
            
            if item['status'] == 'available':
                cart_total += item['total_price']

        return render_template('cart-item.html',
                             cart_items=cart_items,
                             cart_total=cart_total,
                             user=user)

    except Exception as e:
        print(f"Error in cart route: {e}")
        flash('An error occurred while accessing your cart.', 'error')
        return redirect(url_for('index'))
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    if 'loggedin' not in session:
        return jsonify({'status': 'error', 'message': 'Please log in to add items to your cart.'}), 401

    quantity = int(request.form.get('quantity', 1))
    user_id = session['id']
    connection = get_db_connection()
    
    try:
        cursor = connection.cursor()

        # Check if the product exists and get its available quantity
        cursor.execute('SELECT quantity FROM products WHERE product_id = %s', (product_id,))
        product = cursor.fetchone()

        if not product:
            return jsonify({'status': 'error', 'message': 'Product not found!'}), 404

        available_quantity = product[0]

        # Check if the requested quantity exceeds available stock
        if quantity > available_quantity:
            return jsonify({
                'status': 'error', 
                'message': f'Cannot add more than {available_quantity} of this product to your cart.'
            }), 400

        # Check if the product is already in the cart for this user
        cursor.execute('''
            SELECT cart.quantity 
            FROM cart 
            WHERE user_id = %s AND product_id = %s
        ''', (user_id, product_id))
        
        cart_item = cursor.fetchone()

        if cart_item:
            # If product exists in cart, update the quantity
            new_quantity = cart_item[0] + quantity
            if new_quantity > available_quantity:
                return jsonify({
                    'status': 'error',
                    'message': f'Cannot add more than {available_quantity} of this product to your cart.'
                }), 400

            cursor.execute('''
                UPDATE cart 
                SET quantity = %s 
                WHERE user_id = %s AND product_id = %s
            ''', (new_quantity, user_id, product_id))
        else:
            # If product is not in cart, insert new record
            cursor.execute('''
                INSERT INTO cart (user_id, product_id, quantity) 
                VALUES (%s, %s, %s)
            ''', (user_id, product_id, quantity))

        connection.commit()
        return jsonify({
            'status': 'success',
            'message': 'Product added to cart successfully!'
        })

    except Exception as e:
        print(f'Error: {e}')  # Log the error
        return jsonify({
            'status': 'error',
            'message': 'An error occurred while adding to cart. Please try again.'
        }), 500

    finally:
        cursor.close()
        connection.close()



# Add this to your JavaScript file or include in your template
@app.route('/get_cart_count', methods=['GET'])
def get_cart_count():
    if 'loggedin' not in session:
        return jsonify({'count': 0})
        
    connection = get_db_connection()
    try:
        cursor = connection.cursor()
        cursor.execute('''
            SELECT SUM(quantity) 
            FROM cart 
            WHERE user_id = %s
        ''', (session['id'],))
        count = cursor.fetchone()[0] or 0
        return jsonify({'count': count})
    finally:
        cursor.close()
        connection.close()


# Remove from Cart
@app.route('/remove_from_cart/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    if 'loggedin' not in session:
        flash('Please log in to modify your cart.', 'error')
        return redirect(url_for('login'))

    user_id = session['id']
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute('DELETE FROM cart WHERE user_id = %s AND product_id = %s', (user_id, product_id))
    connection.commit()

    cursor.close()
    connection.close()

    flash('Product removed from cart!', 'success')
    return redirect(url_for('view_cart'))


# Update Cart Item Quantity
@app.route('/update_cart/<int:product_id>', methods=['POST'])
def update_cart(product_id):
    if 'loggedin' not in session:
        flash('Please log in to modify your cart.', 'error')
        return redirect(url_for('login'))

    new_quantity = int(request.form.get('quantity', 1))
    user_id = session['id']

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute('UPDATE cart SET quantity = %s WHERE user_id = %s AND product_id = %s',
                   (new_quantity, user_id, product_id))
    connection.commit()

    cursor.close()
    connection.close()

    flash('Cart updated!', 'success')
    return redirect(url_for('view_cart'))


# Clear Cart
@app.route('/clear_cart')
def clear_cart():
    if 'loggedin' not in session:
        flash('Please log in to modify your cart.', 'error')
        return redirect(url_for('login'))

    user_id = session['id']
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute('DELETE FROM cart WHERE user_id = %s', (user_id,))
    connection.commit()

    cursor.close()
    connection.close()

    flash('Cart cleared!', 'success')
    return redirect(url_for('view_cart'))


def validate_phone(phone):
    """Validate phone number format"""
    phone_pattern = re.compile(r'^\d{10}$')
    return bool(phone_pattern.match(phone))

def validate_email(email):
    """Validate email format"""
    email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    return bool(email_pattern.match(email))


@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if 'loggedin' not in session:
        return jsonify({'error': 'Please login to checkout'}), 401

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        # Get selected items from the request
        if request.method == 'GET':
            selected_items = request.args.get('selected_items')
        else:  # POST
            selected_items = request.form.get('selected_items')

        if not selected_items:
            flash('No items selected for checkout.', 'error')
            return redirect(url_for('view_cart'))

        try:
            # Parse the JSON string to list of dictionaries
            selected_items_list = json.loads(selected_items)
            
            # Create a dictionary mapping product_id to quantity
            quantities_map = {str(item['product_id']): int(item['quantity']) 
                            for item in selected_items_list}
            
            # Extract product IDs
            selected_product_ids = list(quantities_map.keys())
            
            print(f"Processed product IDs with quantities: {quantities_map}")  # Debug print
            
            if not selected_product_ids:
                flash('Please select items for checkout.', 'error')
                return redirect(url_for('view_cart'))

        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            flash('Invalid item selection.', 'error')
            return redirect(url_for('view_cart'))

        # Modify the query to use the cart's quantity
        if len(selected_product_ids) == 1:
            query = '''
                SELECT c.*, p.name, p.price, p.image, p.quantity as available_quantity
                FROM cart c 
                JOIN products p ON c.product_id = p.product_id 
                WHERE c.user_id = %s AND c.product_id = %s
            '''
            params = (session['id'], selected_product_ids[0])
        else:
            placeholders = ','.join(['%s'] * len(selected_product_ids))
            query = f'''
                SELECT c.*, p.name, p.price, p.image, p.quantity as available_quantity
                FROM cart c 
                JOIN products p ON c.product_id = p.product_id 
                WHERE c.user_id = %s AND c.product_id IN ({placeholders})
            '''
            params = (session['id'],) + tuple(selected_product_ids)

        print(f"Executing query with params: {params}")  # Debug print
        cursor.execute(query, params)
        cart_items = cursor.fetchall()
        
        # Update quantities based on the selected items
        for item in cart_items:
            item['quantity'] = quantities_map[str(item['product_id'])]

        if not cart_items:
            if request.method == 'GET':
                flash('Your cart is empty. Please add items before checking out.', 'error')
                return redirect(url_for('view_cart'))
            else:
                return jsonify({
                    'error': 'Your cart is empty. Please add items before checking out.',
                    'redirect': url_for('view_cart')
                }), 400

        if request.method == 'GET':
            # Get user data
            cursor.execute('SELECT * FROM users WHERE user_id = %s', (session['id'],))
            user = cursor.fetchone()

            if not user:
                return "User not found", 404
            
            # Calculate cart total
            cart_total = sum(float(item['price']) * item['quantity'] for item in cart_items)

            # Get default address
            cursor.execute('''
                SELECT * FROM user_details 
                WHERE user_id = %s AND is_default = TRUE
                LIMIT 1
            ''', (session['id'],))
            default_address = cursor.fetchone()

            # Pass user_details=None to the template to fix the error
            return render_template('checkout.html',
                    cart_items=cart_items,
                    cart_total=cart_total,
                    default_address=default_address,
                    user=user,
                    user_details=None)  # Add this line to fix the error

        else:  # POST request
            try:
                print("Received POST data:", request.form)
                form_data = request.form.to_dict()

                # Get default address
                cursor.execute('''
                    SELECT * FROM user_details 
                    WHERE user_id = %s AND is_default = TRUE
                    LIMIT 1
                ''', (session['id'],))
                default_address = cursor.fetchone()

                if not default_address:
                        return jsonify({
                            'error': 'No default address found. Please add an address in your profile.'
                        }), 400

                # Validate payment method only
                if not form_data.get('payment_method'):
                    return jsonify({
                        'error': 'Please select a payment method'
                    }), 400

                # Calculate total price
                total_price = sum(float(item['price']) * quantities_map[str(item['product_id'])] 
                                for item in cart_items)

                # Calculate total
                total_price = sum(float(item['price']) * item['quantity'] for item in cart_items)
                print(f"Total price calculated: {total_price}")

                # Create shipping address string from default address
                shipping_address = (
                    f"{default_address['address']}, {default_address['barangay']}, "
                    f"{default_address['city']}, {default_address['province']}, "
                    f"{default_address['postcode']}"
                )

                # Create the order first
                cursor.execute('''
                    INSERT INTO orders 
                    (buyer_id, total_price, shipping_address, payment_method, status, order_date)
                    VALUES (%s, %s, %s, %s, 'pending', NOW())
                ''', (
                    session['id'],
                    total_price,
                    shipping_address,
                    form_data['payment_method']
                ))
                
                # Get the order ID
                order_id = cursor.lastrowid
                print(f"Created order with ID: {order_id}")

                # Now create order items and update stock
                for item in cart_items:
                    quantity = quantities_map[str(item['product_id'])]
                    
                    # Check stock availability
                    if quantity > item['available_quantity']:
                        connection.rollback()
                        return jsonify({
                            'error': f'Not enough stock for {item["name"]}. Only {item["available_quantity"]} available.'
                        }), 400

                    # Create order item
                    cursor.execute('''
                        INSERT INTO order_items 
                        (order_id, product_id, quantity, price)
                        VALUES (%s, %s, %s, %s)
                    ''', (
                        order_id,
                        item['product_id'],
                        quantity,
                        item['price']
                    ))

                    # Update product stock
                    cursor.execute('''
                        UPDATE products 
                        SET quantity = quantity - %s 
                        WHERE product_id = %s
                    ''', (
                        quantity,
                        item['product_id']
                    ))

                # Remove items from cart
                placeholders = ','.join(['%s'] * len(selected_product_ids))
                cursor.execute(f'''
                    DELETE FROM cart 
                    WHERE user_id = %s AND product_id IN ({placeholders})
                ''', (session['id'],) + tuple(selected_product_ids))

                # Commit the transaction
                connection.commit()

                flash('Order placed successfully!', 'success')
                return redirect(url_for('order_confirmation', order_id=order_id))

            except Exception as e:
                print(f"Error processing order: {str(e)}")
                connection.rollback()
                return jsonify({'error': 'Error processing order. Please try again.'}), 500

    except Exception as e:
        print(f"Checkout Error: {str(e)}")
        if connection:
            connection.rollback()
        return jsonify({'error': str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route('/order_confirmation/<int:order_id>')
def order_confirmation(order_id):
    if 'loggedin' not in session:
        return redirect(url_for('login'))
        
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # First get user data
        cursor.execute('SELECT * FROM users WHERE user_id = %s', (session['id'],))
        user = cursor.fetchone()
        
        # Fetch order details
        cursor.execute(''' 
            SELECT o.*, u.name, u.email, 
                GROUP_CONCAT(
                    JSON_OBJECT(
                        'product_id', oi.product_id,
                        'quantity', oi.quantity,
                        'price', oi.price,
                        'name', p.name,
                        'image', p.image
                    )
                ) AS items
            FROM orders o
            JOIN users u ON o.buyer_id = u.user_id
            JOIN order_items oi ON o.order_id = oi.order_id
            JOIN products p ON oi.product_id = p.product_id
            WHERE o.order_id = %s AND o.buyer_id = %s
            GROUP BY o.order_id
        ''', (order_id, session['id']))
        order = cursor.fetchone()

        # Check and parse `items`
        if order and order['items']:
            order['items'] = json.loads(f"[{order['items']}]")  # Wrap in list for JSON parsing
        else:
            order['items'] = []  # Initialize as an empty list if no items

        return render_template('order_confirmation.html', 
                             order=order,
                             user=user)  # Pass user to template
        
    except Error as e:
        print(f"Database error: {e}")
        flash('Error retrieving order details', 'error')
        return redirect(url_for('user_purchase'))
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route('/book_filter', methods=['GET'])
def book_filter():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    category = 'Fiction & Non-Fiction Books'  # Fixed category
    genre = request.args.getlist('genre')
    min_price = request.args.get('min_price')
    max_price = request.args.get('max_price')

    # Validate price parameters
    if min_price and not min_price.isdigit():
        return jsonify({'error': 'Invalid minimum price'}), 400
    if max_price and not max_price.isdigit():
        return jsonify({'error': 'Invalid maximum price'}), 400

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute('SELECT * FROM users WHERE user_id = %s', (session['id'],))
        user = cursor.fetchone()
       
        # Start building the query
        query = """
    SELECT p.*, 
           COALESCE(ROUND(AVG((r.product_quality + r.seller_service + r.delivery_service) / 3), 1), 0) as average_rating,
           COUNT(r.review_id) as rating_count 
    FROM products p 
    LEFT JOIN reviews r ON p.product_id = r.product_id 
    WHERE p.category = %s 
    GROUP BY p.product_id
"""
        params = [category]

        # Add genre filter if provided
        if genre:
            genre_placeholders = ', '.join(['%s'] * len(genre))
            query += f" AND genre IN ({genre_placeholders})"
            params.extend(genre)

        # Add price range filter if both min and max prices are provided
        if min_price and max_price:
            query += " AND price BETWEEN %s AND %s"
            params.extend([min_price, max_price])
        
        cursor.execute(query, params)
        books = cursor.fetchall()

        # Get favorites count
        cursor.execute("SELECT COUNT(*) AS count FROM favorites WHERE user_id = %s", (session['id'],))
        favorites_count = cursor.fetchone()['count']

        return render_template('book-filter.html', 
                             books=books, 
                             favorites_count=favorites_count,
                             user=user)  # Add user to template context

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'An error occurred while fetching data.'}), 500

    finally:
        cursor.close()
        connection.close()

# Category route functions
@app.route('/magazines', methods=['GET'])
def magazine_filter():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    category = 'Magazines & Periodicals'
    min_price = request.args.get('min_price')
    max_price = request.args.get('max_price')
    genre = request.args.getlist('genre')
    
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        # Get user data
        cursor.execute('SELECT * FROM users WHERE user_id = %s', (session['id'],))
        user = cursor.fetchone()
        
        # Get products
        query = """
    SELECT p.*, 
           COALESCE(ROUND(AVG((r.product_quality + r.seller_service + r.delivery_service) / 3), 1), 0) as average_rating,
           COUNT(r.review_id) as rating_count 
    FROM products p 
    LEFT JOIN reviews r ON p.product_id = r.product_id 
    WHERE p.category = %s 
    GROUP BY p.product_id
"""
        params = [category]
        
        if min_price and max_price:
            query += " AND price BETWEEN %s AND %s"
            params.extend([min_price, max_price])
        
        cursor.execute(query, params)
        items = cursor.fetchall()
        
        # Get favorites count
        cursor.execute("SELECT COUNT(*) AS count FROM favorites WHERE user_id = %s", (session['id'],))
        favorites_count = cursor.fetchone()['count']
        
        return render_template('magazine-filter.html', 
                             items=items, 
                             favorites_count=favorites_count,
                             user=user)  # Add user to template context
    
    finally:
        cursor.close()
        connection.close()

@app.route('/music', methods=['GET'])
def music_filter():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
        
    category = 'Music CDs & Vinyl Records'
    min_price = request.args.get('min_price')
    max_price = request.args.get('max_price')
    genre = request.args.getlist('genre')
    
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        # Get user data
        cursor.execute('SELECT * FROM users WHERE user_id = %s', (session['id'],))
        user = cursor.fetchone()
        
        # Get products
        query = """
    SELECT p.*, 
           COALESCE(ROUND(AVG((r.product_quality + r.seller_service + r.delivery_service) / 3), 1), 0) as average_rating,
           COUNT(r.review_id) as rating_count 
    FROM products p 
    LEFT JOIN reviews r ON p.product_id = r.product_id 
    WHERE p.category = %s 
    GROUP BY p.product_id
"""
        params = [category]
        
        if genre:
            genre_placeholders = ', '.join(['%s'] * len(genre))
            query += f" AND genre IN ({genre_placeholders})"
            params.extend(genre)
        
        if min_price and max_price:
            query += " AND price BETWEEN %s AND %s"
            params.extend([min_price, max_price])
        
        cursor.execute(query, params)
        items = cursor.fetchall()
        
        # Get favorites count
        cursor.execute("SELECT COUNT(*) AS count FROM favorites WHERE user_id = %s", (session['id'],))
        favorites_count = cursor.fetchone()['count']
        
        return render_template('music-filter.html', 
                             items=items, 
                             favorites_count=favorites_count,
                             user=user)  # Add user to template context
    
    finally:
        cursor.close()
        connection.close()

@app.route('/movies', methods=['GET'])
def movie_filter():
    if 'loggedin' not in session:
        return redirect(url_for('login'))

    category = 'Movie DVDs & Blu-ray'
    min_price = request.args.get('min_price')
    max_price = request.args.get('max_price')
    genre = request.args.getlist('genre')
    
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        # Get user data
        cursor.execute('SELECT * FROM users WHERE user_id = %s', (session['id'],))
        user = cursor.fetchone()
        
        # Get products
        query = """
    SELECT p.*, 
           COALESCE(ROUND(AVG((r.product_quality + r.seller_service + r.delivery_service) / 3), 1), 0) as average_rating,
           COUNT(r.review_id) as rating_count 
    FROM products p 
    LEFT JOIN reviews r ON p.product_id = r.product_id 
    WHERE p.category = %s 
    GROUP BY p.product_id
"""
        params = [category]
        
        if genre:
            genre_placeholders = ', '.join(['%s'] * len(genre))
            query += f" AND genre IN ({genre_placeholders})"
            params.extend(genre)
        
        if min_price and max_price:
            query += " AND price BETWEEN %s AND %s"
            params.extend([min_price, max_price])
        
        cursor.execute(query, params)
        items = cursor.fetchall()
        
        # Get favorites count
        cursor.execute("SELECT COUNT(*) AS count FROM favorites WHERE user_id = %s", (session['id'],))
        favorites_count = cursor.fetchone()['count']
        
        return render_template('movie-filter.html', 
                             items=items, 
                             favorites_count=favorites_count,
                             user=user)  # Add user to template context
    
    finally:
        cursor.close()
        connection.close()

@app.route('/games', methods=['GET'])
def game_filter():
    if 'loggedin' not in session:
        return redirect(url_for('login'))

    category = 'Video Games & Consoles'
    min_price = request.args.get('min_price')
    max_price = request.args.get('max_price')
    genre = request.args.getlist('genre')
    
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        # Get user data
        cursor.execute('SELECT * FROM users WHERE user_id = %s', (session['id'],))
        user = cursor.fetchone()
        
        # Get products
        query = """
    SELECT p.*, 
           COALESCE(ROUND(AVG((r.product_quality + r.seller_service + r.delivery_service) / 3), 1), 0) as average_rating,
           COUNT(r.review_id) as rating_count 
    FROM products p 
    LEFT JOIN reviews r ON p.product_id = r.product_id 
    WHERE p.category = %s 
    GROUP BY p.product_id
"""
        params = [category]
        
        if genre:
            genre_placeholders = ', '.join(['%s'] * len(genre))
            query += f" AND genre IN ({genre_placeholders})"
            params.extend(genre)
        
        if min_price and max_price:
            query += " AND price BETWEEN %s AND %s"
            params.extend([min_price, max_price])
        
        cursor.execute(query, params)
        items = cursor.fetchall()
        
        # Get favorites count
        cursor.execute("SELECT COUNT(*) AS count FROM favorites WHERE user_id = %s", (session['id'],))
        favorites_count = cursor.fetchone()['count']
        
        return render_template('game-filter.html', 
                             items=items, 
                             favorites_count=favorites_count,
                             user=user)  # Add user to template context
    
    finally:
        cursor.close()
        connection.close()

@app.route('/educational', methods=['GET'])
def educational_filter():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
        
    category = 'Educational DVDs'
    min_price = request.args.get('min_price')
    max_price = request.args.get('max_price')
    
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        # Get user data
        cursor.execute('SELECT * FROM users WHERE user_id = %s', (session['id'],))
        user = cursor.fetchone()
        
        # Get products
        query = """
    SELECT p.*, 
           COALESCE(ROUND(AVG((r.product_quality + r.seller_service + r.delivery_service) / 3), 1), 0) as average_rating,
           COUNT(r.review_id) as rating_count 
    FROM products p 
    LEFT JOIN reviews r ON p.product_id = r.product_id 
    WHERE p.category = %s 
    GROUP BY p.product_id
"""
        params = [category]
        
        if min_price and max_price:
            query += " AND price BETWEEN %s AND %s"
            params.extend([min_price, max_price])
        
        cursor.execute(query, params)
        items = cursor.fetchall()
        
        # Get favorites count
        cursor.execute("SELECT COUNT(*) AS count FROM favorites WHERE user_id = %s", (session['id'],))
        favorites_count = cursor.fetchone()['count']
        
        return render_template('educational-filter.html', 
                             items=items, 
                             favorites_count=favorites_count,
                             user=user)  # Add user to template context
    
    finally:
        cursor.close()
        connection.close()

@app.route('/product/<int:product_id>')
@app.route('/book_detail/<int:product_id>')
def book_detail(product_id):
    if 'loggedin' not in session:
        return redirect(url_for('login'))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        # Get user data
        cursor.execute('SELECT * FROM users WHERE user_id = %s', (session['id'],))
        user = cursor.fetchone()
        
        # Get product details
        cursor.execute("""
            SELECT p.*, 
                ROUND(COALESCE(AVG((r.product_quality + r.seller_service + r.delivery_service) / 3), 0), 1) as average_rating,
                COUNT(DISTINCT r.review_id) as reviews_count
            FROM products p
            LEFT JOIN reviews r ON p.product_id = r.product_id
            WHERE p.product_id = %s
            GROUP BY p.product_id
        """, (product_id,))
        product = cursor.fetchone()
        
        if product:
            # Get reviews with user details
            cursor.execute("""
                SELECT r.*, 
                    u.name,
                    u.email,
                    u.profile_picture,
                    (r.product_quality + r.seller_service + r.delivery_service) / 3 as avg_rating,
                    DATE_FORMAT(r.created_at, '%%M %%d, %%Y') as review_date
                FROM reviews r
                JOIN users u ON r.buyer_id = u.user_id
                WHERE r.product_id = %s
                ORDER BY r.created_at DESC
            """, (product_id,))
            reviews = cursor.fetchall()
            
            product['reviews'] = reviews
            
            # Check if the product is in user's favorites
            cursor.execute("SELECT * FROM favorites WHERE user_id = %s AND product_id = %s", 
                        (session['id'], product_id))
            is_favorite = cursor.fetchone() is not None
            
            # Get related products
            cursor.execute("""
                SELECT p.*,
                    ROUND(COALESCE(AVG((r.product_quality + r.seller_service + r.delivery_service) / 3), 0), 1) as average_rating
                FROM products p
                LEFT JOIN reviews r ON p.product_id = r.product_id
                WHERE p.genre = %s AND p.product_id != %s
                GROUP BY p.product_id
                LIMIT 4
            """, (product['genre'], product_id))
            related_products = cursor.fetchall()
            
            return render_template('book-detail.html', 
                                 product=product, 
                                 is_favorite=is_favorite, 
                                 user=user,
                                 related_products=related_products)
        
        return redirect(url_for('home'))
    finally:
        cursor.close()
        connection.close()


@app.route('/favorites', methods=['GET', 'POST'])
def favorites():
    if 'loggedin' not in session:
        flash('Please log in to view favorites.', 'error')
        return redirect(url_for('login'))

    user_id = session['id']
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        # Get user data
        cursor.execute('SELECT * FROM users WHERE user_id = %s', (user_id,))
        user = cursor.fetchone()
        
        # Get favorites
        cursor.execute("""
            SELECT p.product_id, p.name, p.price, p.image
            FROM favorites f
            JOIN products p ON f.product_id = p.product_id
            WHERE f.user_id = %s
        """, (user_id,))
        favorites_items = cursor.fetchall()
        favorites_count = len(favorites_items)

        return render_template('favorites.html', 
                             favorites_items=favorites_items, 
                             favorites_count=favorites_count,
                             user=user)  # Add user to template context

    finally:
        cursor.close()
        connection.close()

@app.route('/add_to_favorites/<int:product_id>', methods=['POST'])
def add_to_favorites(product_id):
    user_id = session['id']
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        # Add debug print statements
        print(f"Adding to favorites - User ID: {user_id}, Product ID: {product_id}")
        
        cursor.execute("SELECT COUNT(*) FROM favorites WHERE user_id = %s AND product_id = %s", (user_id, product_id))
        count = cursor.fetchone()[0]
        print(f"Existing count: {count}")
        
        if count == 0:
            cursor.execute("INSERT INTO favorites (user_id, product_id) VALUES (%s, %s)", (user_id, product_id))
            connection.commit()
            flash("Product successfully added to favorites!", "success")
        else:
            flash("Product is already in favorites!", "info")

    except Exception as e:
        connection.rollback()
        print(f"Error details: {str(e)}")  # Add detailed error logging
        flash(f"Error adding product to favorites: {str(e)}", "danger")
    finally:
        cursor.close()
        connection.close()

    return redirect(url_for('favorites'))


@app.route('/get/favorites_count', methods=['GET'])
def get_favorites_count():
    user_id = session.get('id')
    if not user_id:
        return jsonify({"count": 0})  # Return 0 instead of an error
    
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM favorites WHERE user_id = %s", (user_id,))
    count = cursor.fetchone()[0]
    cursor.close()
    connection.close()
    
    return jsonify(count=count)



@app.route('/remove_from_favorites', methods=['POST'])
def remove_from_favorites():
    user_id = session['id']
    product_id = request.form.get('product_id')

    if not product_id:
        flash("Product ID not found.", "danger")
        return redirect(url_for('favorites'))

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("DELETE FROM favorites WHERE user_id = %s AND product_id = %s", (user_id, product_id))
        affected_rows = cursor.rowcount
        connection.commit()

        if affected_rows > 0:
            flash("Product successfully removed from favorites!", "success")
        else:
            flash("No product found to remove from favorites.", "warning")

    except Exception as e:
        connection.rollback()
        flash(f"Error removing product from favorites: {str(e)}", "danger")
    
    finally:
        cursor.close()
        connection.close()

    return redirect(url_for('favorites'))


def get_related_products(product_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        # Get the current product's genre
        cursor.execute('SELECT genre FROM products WHERE product_id = %s', (product_id,))
        current_product = cursor.fetchone()
        
        if not current_product:
            return []

        # Fetch related products with the same genre
        cursor.execute('''
            SELECT 
                p.product_id,
                p.name,
                p.price,
                COALESCE(p.image, 'default.jpg') as image,  # Use COALESCE to handle NULL
                p.average_rating,
                p.rating_count
            FROM products p
            WHERE p.genre = %s 
                AND p.product_id != %s 
                AND p.status = 'available'
            LIMIT 5
        ''', (current_product['genre'], product_id))
        
        related_products = cursor.fetchall()

        # Format the products for display
        formatted_products = []
        for product in related_products:
            formatted_products.append({
                'product_id': product['product_id'],
                'name': product['name'],
                'price': float(product['price']) if product['price'] else 0,
                'image': product['image'],
                'average_rating': float(product['average_rating']) if product['average_rating'] else 0,
                'rating_count': product['rating_count'] or 0
            })

        return formatted_products

    finally:
        cursor.close()
        connection.close()


def get_product_reviews(product_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    # Query to fetch reviews for the specified product
    cursor.execute('SELECT * FROM reviews WHERE product_id = %s', (product_id,))
    
    reviews = cursor.fetchall()  # Fetch all reviews
    cursor.close()
    connection.close()

    # Convert the fetched reviews to a list of dictionaries for easier handling
    return [{'customer_name': review[1], 'review_text': review[2], 'rating': review[3], 'review_date': review[4]} for review in reviews]

@app.route('/seller')
def seller():
    if 'id' not in session:
        return redirect(url_for('login'))
        
    user_id = session.get('id')
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    # Get order statistics with COALESCE to handle NULL values
    cursor.execute('''
        SELECT 
            COUNT(DISTINCT CASE WHEN o.status = 'pending' THEN o.order_id END) as to_ship,
            COUNT(DISTINCT CASE WHEN o.status = 'canceled' THEN o.order_id END) as cancelled,
            COUNT(DISTINCT CASE WHEN o.status = 'return' THEN o.order_id END) as returns,
            COUNT(*) as total_orders,
            COALESCE(SUM(o.total_price), 0) as total_revenue
        FROM orders o
        JOIN order_items oi ON o.order_id = oi.order_id
        JOIN products p ON oi.product_id = p.product_id
        WHERE p.seller_id = %s
        GROUP BY p.seller_id
    ''', (user_id,))
    
    stats = cursor.fetchone()
    
    # Handle potential None values in stats
    if stats is None:
        stats = {
            'to_ship': 0,
            'cancelled': 0,
            'returns': 0,
            'total_orders': 0,
            'total_revenue': 0
        }
    else:
        # Ensure all values are numbers, not None
        stats = {
            'to_ship': stats['to_ship'] or 0,
            'cancelled': stats['cancelled'] or 0,
            'returns': stats['returns'] or 0,
            'total_orders': stats['total_orders'] or 0,
            'total_revenue': float(stats['total_revenue'] or 0)
        }
    
    # Get recent orders
    cursor.execute('''
        SELECT DISTINCT
            o.order_id, 
            GROUP_CONCAT(p.name SEPARATOR ', ') as product_name, 
            o.total_price, 
            COALESCE(o.status, 'pending') as status,
            o.payment_method,
            o.order_date
        FROM orders o
        JOIN order_items oi ON o.order_id = oi.order_id
        JOIN products p ON oi.product_id = p.product_id
        WHERE p.seller_id = %s
        GROUP BY o.order_id, o.total_price, o.status, o.payment_method, o.order_date
        ORDER BY o.order_date DESC
        LIMIT 5
    ''', (user_id,))
    
    recent_orders = cursor.fetchall() or []  # Return empty list if None
    
    # Get total customers with safe handling
    cursor.execute('''
        SELECT COUNT(DISTINCT o.buyer_id) as total_customers
        FROM orders o
        JOIN order_items oi ON o.order_id = oi.order_id
        JOIN products p ON oi.product_id = p.product_id
        WHERE p.seller_id = %s
    ''', (user_id,))
    
    result = cursor.fetchone()
    customer_count = result['total_customers'] if result else 0
    
    # Fetch user data with safe handling
    cursor.execute('SELECT * FROM users WHERE user_id = %s', (user_id,))
    user = cursor.fetchone()
    if user is None:
        # Handle case where user is not found
        return redirect(url_for('login'))

    cursor.close()
    connection.close()
    
    return render_template('seller-dashboard.html',
                         user=user,
                         stats=stats,
                         recent_orders=recent_orders,
                         customer_count=customer_count)

from mysql.connector.errors import IntegrityError
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/seller_products')
def seller_products():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
        
    seller_id = session.get('id')
    if not seller_id:
        flash("Please log in first", "error")
        return redirect(url_for('login'))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        # Get user data
        cursor.execute('SELECT * FROM users WHERE user_id = %s', (seller_id,))
        user = cursor.fetchone()
        
        if not user:
            flash("User not found", "error")
            return redirect(url_for('login'))
            
        # Set default profile picture if none exists
        if not user.get('profile_picture'):
            user['profile_picture'] = 'default.jpg'

        selected_category = request.args.get('category')

        # Define base query for products
        query = """
            SELECT 
                product_id,
                seller_id,
                name,
                author,
                category,
                description,
                original_price,
                discount_percentage,
                price,
                quantity,
                image,
                created_at,
                status,
                average_rating,
                rating_count,
                likes_count,
                genre
            FROM products 
            WHERE seller_id = %s
        """

        # Modify query if category is selected
        if selected_category:
            query += " AND category = %s ORDER BY product_id DESC"
            cursor.execute(query, (seller_id, selected_category))
        else:
            query += " ORDER BY product_id DESC"
            cursor.execute(query, (seller_id,))

        products = cursor.fetchall()

        # Convert decimal values to float for JSON serialization
        for product in products:
            if product:
                product['original_price'] = float(product['original_price']) if product['original_price'] else 0
                product['price'] = float(product['price']) if product['price'] else 0
                product['discount_percentage'] = int(product['discount_percentage']) if product['discount_percentage'] else 0
                product['average_rating'] = float(product['average_rating']) if product['average_rating'] else 0

        return render_template('seller-product.html', 
                             products=products if products else [], 
                             seller_id=seller_id,
                             user=user)

    except Exception as e:
        print(f"Error loading products: {str(e)}")
        flash(f"Error loading products: {str(e)}", "error")
        return redirect(url_for('login'))
    
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route('/add_product', methods=['POST'])
def add_product():
    if 'loggedin' not in session or 'id' not in session:
        flash("Please log in first", "error")
        return redirect(url_for('login'))

    try:
        # Create database connection
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # First verify the user exists and is a seller
        cursor.execute('''
            SELECT user_id, is_seller 
            FROM users 
            WHERE user_id = %s
        ''', (session['id'],))
        
        user = cursor.fetchone()
        if not user:
            flash("User not found.", "error")
            return redirect(url_for('login'))
            
        if not user.get('is_seller'):
            flash("You do not have seller privileges.", "error")
            return redirect(url_for('seller_products'))

        # Collect and validate form data
        product_data = {
            'name': request.form.get('product-name', '').strip(),
            'author': request.form.get('product-author', '').strip(),
            'category': request.form.get('product-category', '').strip(),
            'genre': request.form.get('product-genre', '').strip(),
            'original_price': request.form.get('product-original-price'),
            'discount_percentage': request.form.get('product-discount-percentage', '0'),
            'quantity': request.form.get('product-quantity'),
            'description': request.form.get('product-description', '').strip()
        }

        # Validate required fields - Fixed syntax error here
        if not all([
            product_data['name'],
            product_data['original_price'],
            product_data['quantity']
        ]):  # Fixed closing bracket alignment
            flash("Required fields are missing.", "error")
            return redirect(url_for('seller_products'))

        # Convert and validate numerical fields
        try:
            original_price = float(product_data['original_price'])
            discount_percentage = float(product_data['discount_percentage'])
            quantity = int(product_data['quantity'])
            
            if original_price < 0 or discount_percentage < 0 or discount_percentage > 100 or quantity < 0:
                raise ValueError("Invalid numerical values")
                
            discounted_price = original_price * (1 - discount_percentage / 100)
        except ValueError as e:
            flash(f"Invalid numerical values: {str(e)}", "error")
            return redirect(url_for('seller_products'))

        # Handle image upload
        filename = 'default_image.jpg'
        if 'product-image' in request.files:
            image = request.files['product-image']
            if image and image.filename != '' and allowed_file(image.filename):
                filename = secure_filename(image.filename)
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                image.save(image_path)

        # Begin transaction for product insertion
        cursor.execute("START TRANSACTION")
        try:
            # Insert the product with explicit seller_id from session
            cursor.execute("""
                INSERT INTO products (seller_id, name, author, category, genre, original_price, 
                discount_percentage, price, quantity, description, image, status) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                user['user_id'],  # Use verified user_id from database query
                product_data['name'],
                product_data['author'],
                product_data['category'],
                product_data['genre'],
                original_price,
                discount_percentage,
                discounted_price,
                quantity,
                product_data['description'],
                filename,
                'available'
            ))
            
            conn.commit()
            flash('Product added successfully!', 'success')
            
        except mysql.connector.Error as e:
            conn.rollback()
            flash(f"Database error: {str(e)}", "error")
            print(f"Database error details: {e}")
            return redirect(url_for('seller_products'))
            
    except Exception as e:
        flash(f"Error adding product: {str(e)}", "error")
        print(f"General error details: {e}")
        return redirect(url_for('seller_products'))
        
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

    return redirect(url_for('seller_products'))

@app.route('/update_product/<int:product_id>', methods=['POST'])
def update_product(product_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Collect form data
        product_name = request.form.get('product-name')
        product_author = request.form.get('product-author')
        product_category = request.form.get('product-category')
        product_genre = request.form.get('product-genre')
        product_original_price = float(request.form.get('product-original-price'))
        product_discount_percentage = float(request.form.get('product-discount-percentage', 0))
        product_quantity = int(request.form.get('product-quantity'))
        product_description = request.form.get('product-description')

        # Calculate new discounted price
        discounted_price = product_original_price * (1 - product_discount_percentage / 100)

        # Handle image update if new image is provided
        if 'product-image' in request.files and request.files['product-image'].filename != '':
            image = request.files['product-image']
            if image and allowed_file(image.filename):
                filename = secure_filename(image.filename)
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                
                # Update including image
                cursor.execute("""
                    UPDATE products
                    SET name = %s, author = %s, category = %s, genre = %s, 
                        original_price = %s, discount_percentage = %s, price = %s,
                        quantity = %s, description = %s, image = %s
                    WHERE product_id = %s
                """, (
                    product_name, product_author, product_category, product_genre,
                    product_original_price, product_discount_percentage, discounted_price,
                    product_quantity, product_description, filename, product_id
                ))
        else:
            # Update without changing image
            cursor.execute("""
                UPDATE products
                SET name = %s, author = %s, category = %s, genre = %s, 
                    original_price = %s, discount_percentage = %s, price = %s,
                    quantity = %s, description = %s
                WHERE product_id = %s
            """, (
                product_name, product_author, product_category, product_genre,
                product_original_price, product_discount_percentage, discounted_price,
                product_quantity, product_description, product_id
            ))

        conn.commit()
        flash('Product updated successfully!', 'success')

    except Exception as e:
        conn.rollback()
        flash(f"Error updating product: {str(e)}", "error")
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('seller_products'))



@app.route('/delete_product/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM products WHERE product_id = %s", (product_id,))
        conn.commit()

        if cursor.rowcount == 0:
            flash("Product not found or already deleted.", "warning")
        else:
            flash("Product deleted successfully.", "success")
    except Exception as e:
        flash(f"An error occurred: {str(e)}", "danger")
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('seller_products'))

@app.route('/bulk_upload', methods=['POST'])
def bulk_upload():
    if 'csv-file' not in request.files:
        flash('No file part')
        return redirect(request.url)

    csv_file = request.files['csv-file']
    
    # Check if a file was uploaded
    if csv_file.filename == '':
        flash('No selected file')
        return redirect(request.url)

    # Check if the file is a CSV
    if csv_file and csv_file.filename.endswith('.csv'):
        filename = secure_filename(csv_file.filename)
        csv_file.save(f'static/uploads/{filename}')  # Save the file temporarily

        # Process the CSV file
        with open(f'static/uploads/{filename}', newline='') as csvfile:
            csv_reader = csv.reader(csvfile)
            next(csv_reader)  # Skip the header row if present

            # Create a database connection
            conn = get_db_connection()
            cursor = conn.cursor()

            for row in csv_reader:
                # Adjust according to your CSV structure
                product_name = row[0]  # Assuming product name is in the first column
                product_category = row[1]  # Assuming category is in the second column
                product_genre = row[2]  # Assuming genre is in the third column
                product_original_price = row[3]  # And so on...
                product_discount_percentage = row[4]
                product_price = row[5]
                product_quantity = row[6]
                product_description = row[7]
                product_image = row[8]  # If you have images in the CSV
                seller_id = row[9]  # Assuming seller_id is in the tenth column

                try:
                    cursor.execute("""
                        INSERT INTO products (name, category, genre, original_price, discount_percentage, price, quantity, description, image, seller_id)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (product_name, product_category, product_genre, product_original_price, product_discount_percentage, product_price, product_quantity, product_description, product_image, seller_id))
                except IntegrityError as e:
                    conn.rollback()
                    flash(f"Error uploading product: {e}")
                    continue

            conn.commit()
            cursor.close()
            conn.close()

        flash('Products uploaded successfully!')
        return redirect(url_for('seller'))  # Redirect to the seller dashboard or any other page
    else:
        flash('Invalid file format. Please upload a CSV file.')
        return redirect(request.url)

@app.route('/seller_dashboard')
def seller_dashboard():
    if 'id' not in session:
        return redirect(url_for('login'))
        
    user_id = session.get('id')
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        # First, get the user data
        cursor.execute('SELECT * FROM users WHERE user_id = %s', (user_id,))
        user = cursor.fetchone()
        
        if not user:
            flash('User not found', 'error')
            return redirect(url_for('login'))
            
        if not user['is_seller']:
            flash('Seller access required', 'error')
            return redirect(url_for('home'))

        # Get seller's total revenue and orders
        cursor.execute('''
            SELECT 
                COALESCE(SUM(oi.price * oi.quantity), 0) as total_revenue,
                COUNT(DISTINCT o.order_id) as total_orders
            FROM products p
            LEFT JOIN order_items oi ON p.product_id = oi.product_id
            LEFT JOIN orders o ON oi.order_id = o.order_id
            WHERE p.seller_id = %s AND (o.status != 'cancelled' OR o.status IS NULL)
        ''', (user_id,))
        
        basic_stats = cursor.fetchone()
        
        # Calculate repeat purchase rate
        cursor.execute('''
            WITH customer_orders AS (
                SELECT 
                    o.buyer_id,
                    COUNT(DISTINCT o.order_id) as order_count
                FROM products p
                JOIN order_items oi ON p.product_id = oi.product_id
                JOIN orders o ON oi.order_id = o.order_id
                WHERE p.seller_id = %s
                GROUP BY o.buyer_id
            )
            SELECT 
                COALESCE(
                    (COUNT(CASE WHEN order_count > 1 THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0)),
                    0
                ) as repeat_rate
            FROM customer_orders
        ''', (user_id,))
        
        repeat_rate = cursor.fetchone()
        
        # Get total customers
        cursor.execute('''
            SELECT COUNT(DISTINCT o.buyer_id) as total_customers
            FROM products p
            JOIN order_items oi ON p.product_id = oi.product_id
            JOIN orders o ON oi.order_id = o.order_id
            WHERE p.seller_id = %s
        ''', (user_id,))
        
        customer_stats = cursor.fetchone()
        
        # Get monthly sales data for chart
        cursor.execute('''
            SELECT 
                DATE_FORMAT(o.order_date, '%Y-%m') as month,
                COALESCE(SUM(oi.price * oi.quantity), 0) as monthly_revenue
            FROM products p
            JOIN order_items oi ON p.product_id = oi.product_id
            JOIN orders o ON oi.order_id = o.order_id
            WHERE p.seller_id = %s
                AND o.order_date >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)
                AND o.status != 'cancelled'
            GROUP BY DATE_FORMAT(o.order_date, '%Y-%m')
            ORDER BY month ASC
        ''', (user_id,))
        
        chart_data = cursor.fetchall()
        
        # Prepare chart data
        months = []
        revenues = []
        for data in chart_data:
            months.append(datetime.strptime(data['month'], '%Y-%m').strftime('%b %Y'))
            revenues.append(float(data['monthly_revenue']))
        
        # If no chart data, provide default values
        if not months:
            months = [datetime.now().strftime('%b %Y')]
            revenues = [0]
        
        # Combine all stats
        stats = {
            'total_revenue': basic_stats['total_revenue'] or 0,
            'total_orders': basic_stats['total_orders'] or 0,
            'repeat_purchase_rate': round(repeat_rate['repeat_rate'] or 0, 1),
            'total_customers': customer_stats['total_customers'] or 0
        }
        
        # Update the top selling products query in your seller_dashboard route
        cursor.execute('''
            SELECT 
                p.product_id,
                p.name,
                p.price,
                p.image as image_path,  -- Changed from p.image_path to p.image
                COUNT(DISTINCT o.order_id) as order_count,
                SUM(oi.quantity) as total_quantity
            FROM products p
            INNER JOIN order_items oi ON p.product_id = oi.product_id
            INNER JOIN orders o ON oi.order_id = o.order_id
            WHERE p.seller_id = %s 
                AND o.status != 'cancelled'
                AND o.status != 'pending'
            GROUP BY 
                p.product_id,
                p.name,
                p.price,
                p.image  -- Changed from p.image_path to p.image
            ORDER BY total_quantity DESC, order_count DESC
            LIMIT 5
        ''', (user_id,))

        top_products = cursor.fetchall()

        # Add debug print to check the data
        print("Top Products Query Result:", top_products)
        
        return render_template('seller-dashboard.html',
                             user=user,  # Added user to template context
                             stats=stats,
                             months=months,
                             sales_data=revenues,
                             top_products=top_products)
                             
    except Exception as e:
        print(f"Error in seller dashboard: {str(e)}")
        flash('Error loading dashboard data', 'error')
        return redirect(url_for('home'))
        
    finally:
        cursor.close()
        connection.close()

@app.route('/seller_customers')
def seller_customers():
    if 'id' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('login'))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        # Debug: Log the user ID
        print(f"Current seller ID: {session['id']}")
        
        # First, verify if the user is a seller and get user data
        cursor.execute('SELECT * FROM users WHERE user_id = %s', (session['id'],))
        user = cursor.fetchone()
        
        if not user or not user['is_seller']:
            flash('Seller access required', 'error')
            return redirect(url_for('home'))
            
        # Use session['id'] instead of undefined seller_id
        cursor.execute('''
            SELECT 
                u.user_id,
                u.name,
                u.email,
                MIN(o.order_date) as first_order_date,
                COUNT(DISTINCT o.order_id) as total_orders,
                COALESCE(SUM(oi.quantity * oi.price), 0) as total_spent
            FROM users u
            INNER JOIN orders o ON u.user_id = o.buyer_id
            INNER JOIN order_items oi ON o.order_id = oi.order_id
            INNER JOIN products p ON oi.product_id = p.product_id
            WHERE p.seller_id = %s 
                AND u.is_admin = 0 
            GROUP BY u.user_id, u.name, u.email
            ORDER BY total_spent DESC
        ''', (session['id'],))  # Changed this line
        
        customers = cursor.fetchall()
        
        # Convert first_order_date to datetime object if it exists
        for customer in customers:
            if customer['first_order_date']:
                customer['first_order_date'] = datetime.strptime(
                    customer['first_order_date'].strftime('%Y-%m-%d'), 
                    '%Y-%m-%d'
                )
            else:
                customer['first_order_date'] = None
                
        return render_template('seller-customers.html', 
                             customers=customers,
                             current_date=datetime.now().strftime('%Y-%m-%d'),
                             user=user)  # Added user to template context
                             
    except Exception as e:
        print(f"Error fetching customers: {str(e)}")
        flash('Error fetching customer data', 'error')
        return redirect(url_for('seller_dashboard'))
        
    finally:
        cursor.close()
        connection.close()

@app.route('/seller_orders', methods=['GET', 'POST'])
def seller_orders():
    if 'id' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('login'))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        # Debug print
        print(f"Current seller ID: {session['id']}")
        
        # First, verify if the user is a seller and get user data
        cursor.execute('SELECT * FROM users WHERE user_id = %s', (session['id'],))
        user = cursor.fetchone()
        
        if not user or not user['is_seller']:
            flash('Seller access required', 'error')
            return redirect(url_for('home'))

        # Rest of your existing seller_orders code...
        cursor.execute('''
            SELECT DISTINCT
                o.order_id,
                GROUP_CONCAT(p.name SEPARATOR ', ') as product_name,
                o.total_price,
                COALESCE(o.status, 'pending') as status,
                o.payment_method,
                o.order_date,
                u.name as buyer_name,
                u.user_id as buyer_id,
                u.email as buyer_email
            FROM orders o
            JOIN order_items oi ON o.order_id = oi.order_id
            JOIN products p ON oi.product_id = p.product_id
            LEFT JOIN users u ON o.buyer_id = u.user_id
            WHERE p.seller_id = %s
            GROUP BY 
                o.order_id, 
                o.total_price, 
                o.status, 
                o.payment_method, 
                o.order_date,
                u.name,
                u.user_id,
                u.email
            ORDER BY o.order_date DESC
        ''', (session['id'],))
        
        all_orders = cursor.fetchall()
        
        # Organize orders by status
        orders_by_status = {
            'pending': [],
            'processing': [],
            'shipped': [],
            'completed': [],
            'cancelled': []
        }
        
        for order in all_orders:
            status = order['status'].lower() if order['status'] else 'pending'
            if status in orders_by_status:
                orders_by_status[status].append(order)
                
        # Get status counts
        cursor.execute('''
            SELECT 
                COALESCE(o.status, 'pending') as status,
                COUNT(DISTINCT o.order_id) as count
            FROM orders o
            JOIN order_items oi ON o.order_id = oi.order_id
            JOIN products p ON oi.product_id = p.product_id
            WHERE p.seller_id = %s
            GROUP BY o.status
        ''', (session['id'],))
        
        status_counts = {row['status'].lower(): row['count'] for row in cursor.fetchall()}
        
        return render_template('seller-orders.html', 
                             all_orders=all_orders,
                             orders_by_status=orders_by_status,
                             status_counts=status_counts,
                             user=user)

    except Exception as e:
        print(f"Error in seller_orders: {str(e)}")
        flash('An error occurred while processing orders', 'error')
        return redirect(url_for('home'))
        
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
            
def notify_buyer(order_id, new_status):
    """
    Notify buyer about order status changes via database notification and email
    Parameters:
    - order_id: int
    - new_status: str
    Returns: bool
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Get order and buyer information
        cursor.execute('''
            SELECT 
                o.order_id,
                o.buyer_id,
                u.email as buyer_email,
                u.name as buyer_name,
                GROUP_CONCAT(p.name SEPARATOR ', ') as products,
                o.total_price
            FROM orders o
            JOIN users u ON o.buyer_id = u.user_id
            JOIN order_items oi ON o.order_id = oi.order_id
            JOIN products p ON oi.product_id = p.product_id
            WHERE o.order_id = %s
            GROUP BY o.order_id, o.buyer_id, u.email, u.name
        ''', (order_id,))
        
        order_info = cursor.fetchone()
        
        if not order_info:
            print(f"Error: Order {order_id} not found")
            return False
            
        # Create notification message
        status_messages = {
            'pending': 'Your order has been received and is pending processing.',
            'processing': 'Your order is now being processed.',
            'shipped': 'Your order has been shipped!',
            'completed': 'Your order has been delivered. Thank you for shopping with us!',
            'cancelled': 'Your order has been cancelled.',
            'return': 'Your return request has been received.'
        }
        
        message = status_messages.get(new_status.lower(), f'Your order status has been updated to: {new_status}')
        
        # Insert notification into database matching your schema
        cursor.execute('''
            INSERT INTO notifications 
                (user_id, type, message, order_id, created_at, is_read)
            VALUES 
                (%s, %s, %s, %s, NOW(), 0)
        ''', (
            order_info['buyer_id'],
            'general',  # type is varchar(50) with default 'general'
            message,    # message is text
            order_id,   # order_id can be NULL
        ))
        
        # Send email notification
        email_subject = f'Order #{order_id} Status Update'
        email_body = f'''
            Dear {order_info['buyer_name']},

            {message}

            Order Details:
            - Order ID: #{order_id}
            - Products: {order_info['products']}
            - Total Amount: ₱{order_info['total_price']}

            You can track your order status in your account dashboard.

            If you have any questions, please don't hesitate to contact us.

            Best regards,
            Your Lithub Team
        '''
        
        send_email(
            to_email=order_info['buyer_email'],
            subject=email_subject,
            body=email_body
        )
        
        connection.commit()
        return True
        
    except Exception as e:
        print(f"Error in notify_buyer: {str(e)}")
        if connection:
            connection.rollback()
        return False
        
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def send_email(to_email, subject, body):
    """
    Helper function to send emails
    """
    try:
        # Email server settings
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        sender_email = "literaryhub5@gmail.com"  # Replace with your email
        sender_password = "vbih iojp zvxk lnob"   # Replace with your app password
        
        # Create message
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = to_email
        
        # Send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
            
        return True
        
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False

@app.route('/seller_notifications')
def seller_notifications():
    if 'id' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('login'))
        
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Get user data
        cursor.execute('SELECT * FROM users WHERE user_id = %s', (session['id'],))
        user = cursor.fetchone()
        
        if not user:
            flash('User not found', 'error')
            return redirect(url_for('login'))
            
        # Get notifications
        cursor.execute('''
            SELECT * FROM notifications 
            WHERE user_id = %s 
            ORDER BY created_at DESC
        ''', (session['id'],))
        notifications = cursor.fetchall()
        
        return render_template('seller-notif.html', 
                             user=user,
                             notifications=notifications)
                             
    except Exception as e:
        print(f"Error in seller notifications: {str(e)}")
        flash('Error loading notifications', 'error')
        return redirect(url_for('home'))
        
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

@app.route('/seller_reports', methods=['GET', 'POST'])
def seller_reports():
    if 'id' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('login'))
        
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Get user data
        cursor.execute('SELECT * FROM users WHERE user_id = %s', (session['id'],))
        user = cursor.fetchone()
        
        if not user:
            flash('User not found', 'error')
            return redirect(url_for('login'))

        # Get date range from form or use default (last 30 days)
        default_from_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        default_to_date = datetime.now().strftime('%Y-%m-%d')
        from_date = request.args.get('fromDate', default_from_date)
        to_date = request.args.get('toDate', default_to_date)

        # Get sales data for chart
        cursor.execute('''
            SELECT 
                DATE_FORMAT(o.order_date, '%Y-%m-%d') as date,
                COUNT(DISTINCT o.order_id) as orders,
                COALESCE(SUM(oi.price * oi.quantity), 0) as revenue
            FROM products p
            INNER JOIN order_items oi ON p.product_id = oi.product_id
            INNER JOIN orders o ON oi.order_id = o.order_id
            WHERE p.seller_id = %s 
                AND o.status != 'cancelled'
                AND DATE(o.order_date) BETWEEN %s AND %s
            GROUP BY DATE(o.order_date)
            ORDER BY date ASC
        ''', (session['id'], from_date, to_date))
        
        sales_data = cursor.fetchall()
        
        # Prepare chart data
        chart_dates = []
        chart_revenues = []
        chart_orders = []
        
        for row in sales_data:
            chart_dates.append(row['date'])
            chart_revenues.append(float(row['revenue']))
            chart_orders.append(row['orders'])

        # Get summary statistics
        cursor.execute('''
            SELECT 
                COUNT(DISTINCT o.order_id) as total_orders,
                COUNT(DISTINCT o.buyer_id) as unique_customers,
                COALESCE(SUM(oi.price * oi.quantity), 0) as total_revenue,
                COALESCE(AVG(oi.price * oi.quantity), 0) as avg_order_value
            FROM products p
            INNER JOIN order_items oi ON p.product_id = oi.product_id
            INNER JOIN orders o ON oi.order_id = o.order_id
            WHERE p.seller_id = %s 
                AND o.status != 'cancelled'
                AND DATE(o.order_date) BETWEEN %s AND %s
        ''', (session['id'], from_date, to_date))
        
        summary_stats = cursor.fetchone()
        
        if summary_stats:
            summary_stats['total_revenue'] = float(summary_stats['total_revenue'])
            summary_stats['avg_order_value'] = float(summary_stats['avg_order_value'])
        
        # Get top selling products
        cursor.execute('''
            SELECT 
                p.name,
                COUNT(DISTINCT o.order_id) as order_count,
                SUM(oi.quantity) as total_quantity,
                COALESCE(SUM(oi.price * oi.quantity), 0) as revenue
            FROM products p
            INNER JOIN order_items oi ON p.product_id = oi.product_id
            INNER JOIN orders o ON oi.order_id = o.order_id
            WHERE p.seller_id = %s 
                AND o.status != 'cancelled'
                AND DATE(o.order_date) BETWEEN %s AND %s
            GROUP BY p.product_id, p.name
            ORDER BY revenue DESC
            LIMIT 5
        ''', (session['id'], from_date, to_date))
        
        top_products = cursor.fetchall()
        
        # Convert Decimal to float for JSON serialization
        for product in top_products:
            product['revenue'] = float(product['revenue'])

        return render_template('seller-reports.html', 
                             user=user,
                             chart_dates=chart_dates,
                             chart_revenues=chart_revenues,
                             chart_orders=chart_orders,
                             summary_stats=summary_stats or {},
                             top_products=top_products,
                             from_date=from_date,
                             to_date=to_date)
                             
    except Exception as e:
        print(f"Error in seller reports: {str(e)}")
        flash('Error loading reports', 'error')
        return redirect(url_for('home'))
        
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

# Add route for generating PDF report
@app.route('/generate_sales_report_pdf')
def generate_sales_report_pdf():
    if 'id' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    try:
        from_date = request.args.get('fromDate')
        to_date = request.args.get('toDate')

        # Get the sales data
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Get seller info
        cursor.execute('SELECT * FROM users WHERE user_id = %s', (session['id'],))
        seller = cursor.fetchone()

        # Get sales summary
        cursor.execute('''
            SELECT 
                COUNT(DISTINCT o.order_id) as total_orders,
                COALESCE(SUM(oi.price * oi.quantity), 0) as total_revenue,
                COUNT(DISTINCT o.buyer_id) as unique_customers
            FROM products p
            INNER JOIN order_items oi ON p.product_id = oi.product_id
            INNER JOIN orders o ON oi.order_id = o.order_id
            WHERE p.seller_id = %s 
                AND o.status != 'cancelled'
                AND DATE(o.order_date) BETWEEN %s AND %s
        ''', (session['id'], from_date, to_date))
        summary = cursor.fetchone()

        # Get detailed product sales data
        cursor.execute('''
            SELECT 
                p.name AS product_name,
                SUM(oi.quantity) AS total_quantity,
                oi.price AS unit_price,
                COALESCE(SUM(oi.price * oi.quantity), 0) AS total_price,
                COUNT(DISTINCT o.buyer_id) AS unique_buyers
            FROM products p
            INNER JOIN order_items oi ON p.product_id = oi.product_id
            INNER JOIN orders o ON oi.order_id = o.order_id
            WHERE p.seller_id = %s 
                AND o.status != 'cancelled'
                AND DATE(o.order_date) BETWEEN %s AND %s
            GROUP BY p.product_id, oi.price
            ORDER BY total_price DESC
        ''', (session['id'], from_date, to_date))
        product_sales = cursor.fetchall()

        # Create PDF using reportlab
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []

        # Add header
        styles = getSampleStyleSheet()
        elements.append(Paragraph(f"Sales Report for {seller['name']}", styles['Title']))
        elements.append(Paragraph(f"Period: {from_date} to {to_date}", styles['Normal']))
        elements.append(Spacer(1, 20))

        # Add summary table
        summary_data = [
            ['Total Orders', 'Total Revenue', 'Unique Customers'],
            [
                str(summary['total_orders']),
                f"₱{summary['total_revenue']:,.2f}",
                str(summary['unique_customers'])
            ]
        ]

        summary_table = Table(summary_data)
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), 'black'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 20))

        # Add product sales table
        product_sales_data = [
            ['Product Name', 'Quantity Sold', 'Unit Price', 'Total Price', 'Unique Buyers']
        ]
        for product in product_sales:
            product_sales_data.append([
                product['product_name'],
                str(product['total_quantity']),
                f"₱{product['unit_price']:,.2f}",
                f"₱{product['total_price']:,.2f}",
                str(product['unique_buyers'])
            ])

        product_sales_table = Table(product_sales_data)
        product_sales_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), 'black'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(product_sales_table)

        # Build PDF
        doc.build(elements)

        # Prepare response
        buffer.seek(0)
        response = make_response(buffer.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=sales_report_{from_date}_to_{to_date}.pdf'

        return response

    except Exception as e:
        print(f"Error generating PDF: {str(e)}")
        return jsonify({'error': 'Failed to generate report'}), 500

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()


def calculate_percentage_change(old_value, new_value):
    if old_value == 0:
        return 100 if new_value > 0 else 0
    return ((new_value - old_value) / old_value) * 100


# Decorator to require admin login
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is logged in as admin
        if 'admin_id' not in session or not session.get('is_admin'):
            flash('Please log in as admin', 'error')
            return redirect(url_for('admin_login'))
            
        # Get admin user data
        admin = get_admin_user()
        if not admin:
            flash('Admin access required', 'error')
            return redirect(url_for('admin_login'))
            
        return f(*args, **kwargs)
    return decorated_function

# Admin dashboard route
def get_admin_user():
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT * FROM users WHERE is_admin = 1 LIMIT 1')
        admin = cursor.fetchone()
        return admin
    except Exception as e:
        print(f"Error getting admin user: {e}")
        return None
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()


def get_dashboard_stats():
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        stats = {}

        # Get total revenue
        cursor.execute('''
            SELECT COALESCE(SUM(total_price), 0) as revenue 
            FROM orders 
            WHERE YEAR(order_date) = YEAR(CURRENT_DATE)
            AND status != 'canceled'
        ''')
        stats['revenue'] = cursor.fetchone()['revenue']

        # Get total commission (assuming 5% commission)
        stats['commission'] = float(stats['revenue']) * 0.05

        # Get total orders
        cursor.execute('''
            SELECT COUNT(*) as total_orders 
            FROM orders 
            WHERE YEAR(order_date) = YEAR(CURRENT_DATE)
            AND status != 'canceled'
        ''')
        stats['orders'] = cursor.fetchone()['total_orders']

        # Get repeat purchase rate - Updated to use buyer_id instead of user_id
        cursor.execute('''
            SELECT 
                (COUNT(DISTINCT CASE WHEN order_count > 1 THEN buyer_id END) * 100.0 / 
                COUNT(DISTINCT buyer_id)) as rate
            FROM (
                SELECT buyer_id, COUNT(*) as order_count 
                FROM orders 
                WHERE YEAR(order_date) = YEAR(CURRENT_DATE)
                AND status != 'canceled'
                GROUP BY buyer_id
            ) as user_orders
        ''')
        result = cursor.fetchone()
        stats['growth_rate'] = round(result['rate'] if result['rate'] else 0, 1)

        # Get total customers
        cursor.execute('SELECT COUNT(*) as total FROM users WHERE is_admin = 0')
        stats['total_customers'] = cursor.fetchone()['total']

        # Get pending applicants
        cursor.execute('SELECT COUNT(*) as pending FROM users WHERE status = "pending"')
        stats['pending_applicants'] = cursor.fetchone()['pending']

        # Get top selling products
        cursor.execute('''
            SELECT 
                p.product_id,
                p.name,
                p.price,
                p.image as image_path,
                COUNT(o.order_id) as order_count
            FROM products p
            LEFT JOIN order_items o ON p.product_id = o.product_id
            LEFT JOIN orders ord ON o.order_id = ord.order_id
            WHERE YEAR(ord.order_date) = YEAR(CURRENT_DATE)
            AND ord.status != 'canceled'
            GROUP BY p.product_id, p.name, p.price, p.image
            ORDER BY order_count DESC
            LIMIT 3
        ''')
        stats['top_products'] = cursor.fetchall()

        return stats

    except Exception as e:
        print(f"Error in get_dashboard_stats: {str(e)}")
        raise e

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    try:
        # Get user data
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Get admin user data using session ID
        cursor.execute('SELECT * FROM users WHERE user_id = %s AND is_admin = 1', 
                      (session['admin_id'],))
        user = cursor.fetchone()
        
        if not user:
            session.clear()
            flash('Admin user not found', 'error')
            return redirect(url_for('admin_login'))

        # Get dashboard statistics
        stats = get_dashboard_stats()
        
        # Get current date for display
        current_date = datetime.now().strftime('%B %d, %Y')
        
        # Get monthly sales data for chart
        cursor.execute('''
            SELECT 
                MONTH(order_date) as month,
                COALESCE(SUM(total_price), 0) as total_sales
            FROM orders 
            WHERE YEAR(order_date) = YEAR(CURRENT_DATE)
            AND status != 'canceled'
            GROUP BY MONTH(order_date)
            ORDER BY month
        ''')
        monthly_sales = cursor.fetchall()
        
        # Prepare data for charts
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        sales_data = {
            "labels": months,
            "revenue": [float(row['total_sales']) for row in monthly_sales],
            "current_week": 0,
            "previous_week": 0
        }
        
        return render_template('admin-dashboard.html',
                             user=user,  # Add user to template context
                             stats=stats,
                             current_date=current_date,
                             months=months,
                             sales_data=sales_data,
                             top_products=stats['top_products'])  # Add this line

    except Exception as e:
        print(f"Dashboard Error: {str(e)}")
        flash('An error occurred while loading dashboard data', 'error')
        return redirect(url_for('admin_login'))

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()


# Route for managing sellers
@app.route('/sellers')
@admin_required
def admin_sellers():
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Get admin user data
        cursor.execute('SELECT * FROM users WHERE is_admin = 1')
        users = cursor.fetchall()
        user = users[0] if users else {}
        
        # Get seller requests
        cursor.execute('''
            SELECT sr.*, u.name, u.email 
            FROM seller_requests sr 
            JOIN users u ON sr.user_id = u.user_id 
            ORDER BY sr.request_date DESC
        ''')
        requests = cursor.fetchall()
        
        return render_template('admin-seller.html', 
                             requests=requests,
                             user=user)  # Add user to template context
        
    except Error as e:
        print(f"Error: {e}")
        return "An error occurred", 500
    finally:
        cursor.close()
        connection.close()

# Route for handling seller requests (approve or reject)
@app.route('/admin/seller-request/reject/<int:request_id>', methods=['POST'])
@admin_required
def reject_seller_request(request_id):
    try:
        data = request.get_json()
        rejection_reason = data.get('reason', '')
        additional_comments = data.get('comments', '')

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Fetch user details
        cursor.execute('''
            SELECT sr.user_id, u.name, u.email 
            FROM seller_requests sr
            JOIN users u ON sr.user_id = u.user_id
            WHERE sr.request_id = %s
        ''', (request_id,))
        user_info = cursor.fetchone()
        
        if not user_info:
            return jsonify({'error': 'User not found'}), 404
        
        # Update seller_requests table with rejection
        cursor.execute('''
            UPDATE seller_requests 
            SET status = 'rejected',
                processed_date = CURRENT_TIMESTAMP,
                rejection_reason = %s,
                additional_comments = %s
            WHERE request_id = %s AND status = 'pending'
        ''', (rejection_reason, additional_comments, request_id))
        
        if cursor.rowcount == 0:
            return jsonify({'error': 'Request not found or already processed'}), 404
        
        # Create rejection notification message
        notification_message = f'''Dear {user_info['name']},
Your seller registration request has been declined for the following reason:
{rejection_reason}

Additional Comments:
{additional_comments if additional_comments else 'No additional comments provided.'}

You can submit a new application after 30 days with complete documentation.
If you have any questions, please contact our support team.'''
        
        # Insert notification
        cursor.execute('''
            INSERT INTO notifications (
                user_id, 
                type, 
                message, 
                created_at, 
                is_read
            ) VALUES (%s, %s, %s, NOW(), 0)
        ''', (user_info['user_id'], 'seller_request', notification_message))
        
        # Send email notification
        msg = Message(
            'Seller Registration Request Declined',
            recipients=[user_info['email']]
        )
        msg.body = notification_message
        mail.send(msg)
        
        connection.commit()
        
        return jsonify({
            'message': 'Seller request rejected successfully',
            'request_id': request_id,
            'status': 'rejected'
        })
        
    except Exception as e:
        if connection:
            connection.rollback()
        return jsonify({'error': str(e)}), 500
        
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

# Other admin routes
@app.route('/admin_customers')
@admin_required
def admin_customers():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        # Get admin user data
        cursor.execute('SELECT * FROM users WHERE user_id = %s AND is_admin = 1', 
                      (session['admin_id'],))
        user = cursor.fetchone()
        
        if not user:
            flash('Admin user not found', 'error')
            return redirect(url_for('admin_login'))
        
        # Get customer information with their first order date and total orders/spent
        cursor.execute('''
            SELECT 
                u.user_id,
                u.name,
                u.email,
                MIN(o.order_date) as first_order_date,
                COUNT(o.order_id) as total_orders,
                COALESCE(SUM(o.total_price), 0) as total_spent
            FROM users u
            LEFT JOIN orders o ON u.user_id = o.buyer_id
            WHERE u.is_admin = 0 
            GROUP BY u.user_id, u.name, u.email
            ORDER BY u.name
        ''')
        
        customers = cursor.fetchall()
        
        # Convert first_order_date to datetime object if it exists
        for customer in customers:
            if customer['first_order_date']:
                customer['first_order_date'] = datetime.strptime(
                    customer['first_order_date'].strftime('%Y-%m-%d'), 
                    '%Y-%m-%d'
                )
            else:
                customer['first_order_date'] = None
                
        return render_template('admin-customer.html', 
                             customers=customers,
                             current_date=datetime.now().strftime('%Y-%m-%d'),
                             user=user)  # Pass the user data to template
        
    except Exception as e:
        print(f"Error fetching customer data: {e}")
        flash('Error fetching customer data', 'error')
        return redirect(url_for('admin_dashboard'))
        
    finally:
        cursor.close()
        connection.close()

@app.route('/notifications')
@admin_required
def admin_notifications():
    user = get_admin_user()  # Get the admin user data
    return render_template('admin-notif.html', user=user)

@app.route('/admin/messages')
@admin_required
def admin_messages():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    
        # Get admin user data
    cursor.execute('SELECT * FROM users WHERE user_id = %s AND is_admin = 1', 
                      (session['admin_id'],))
    user = cursor.fetchone()
        
    if not user:
            flash('Admin user not found', 'error')
            return redirect(url_for('admin_login'))

    # Fetch messages including the message_id
    cursor.execute('''
        SELECT message_id, name, email, phone, message, created_at, status 
        FROM contact_messages 
        ORDER BY created_at DESC
    ''')
    messages = cursor.fetchall()
    
    cursor.close()
    connection.close()

    return render_template('admin-messages.html', messages=messages, user=user)  # Pass user to the template

@app.route('/admin/reply/<int:message_id>', methods=['POST'])
@admin_required
def admin_reply_message(message_id):
    reply_text = request.form.get('reply')
    if not reply_text:
        flash('Reply text cannot be empty', 'error')
        return redirect(url_for('admin_messages'))
        
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True, buffered=True)  # Use buffered cursor
        
        # Get the contact message and user details
        cursor.execute('''
            SELECT cm.*, u.email, u.name, u.user_id 
            FROM contact_messages cm
            LEFT JOIN users u ON cm.user_id = u.user_id 
            WHERE cm.message_id = %s
        ''', (message_id,))
        
        contact_message = cursor.fetchone()
        if not contact_message:
            flash('Message not found', 'error')
            return redirect(url_for('admin_messages'))

        try:
            # Update contact message status
            cursor.execute('''
                UPDATE contact_messages 
                SET status = 'replied' 
                WHERE message_id = %s
            ''', (message_id,))
            
            # Create chat message for the reply
            cursor.execute('''
                INSERT INTO chat_messages 
                (sender_id, receiver_id, message, status, is_admin_reply, is_reply) 
                VALUES (%s, %s, %s, 'unread', TRUE, TRUE)
            ''', (session.get('admin_id'), contact_message['user_id'], reply_text))
            new_message_id = cursor.lastrowid
            
            # Create chat message status
            cursor.execute('''
                INSERT INTO chat_message_status 
                (message_id, user_id, is_read) 
                VALUES (%s, %s, FALSE)
            ''', (new_message_id, contact_message['user_id']))
            
            # Create notification
            notification_message = f'<a href="{url_for("chat_messages")}">New message from admin: {reply_text[:50]}{"..." if len(reply_text) > 50 else ""}</a>'
            create_notification(
                user_id=contact_message['user_id'],
                message=notification_message,
                notification_type='chat_message'
            )
            
            # Send email notification if email exists
            if contact_message.get('email'):
                try:
                    msg = Message(
                        'New Message from LitHub Support',
                        sender=('LitHub Support', 'lithubadmin@gmail.com'),
                        recipients=[contact_message['email']],
                        body=f"""Dear {contact_message.get('name', 'Customer')},

You have received a new message from LitHub Support:

{reply_text}

View your messages at: {url_for('chat_messages', _external=True)}

Best regards,
LitHub Support Team"""
                    )
                    mail.send(msg)
                except Exception as e:
                    print(f"Email error in admin_reply: {str(e)}")
                    # Continue with transaction even if email fails
            
            connection.commit()
            flash('Reply sent successfully', 'success')
            
        except Exception as e:
            connection.rollback()
            print(f"Transaction error in admin_reply: {str(e)}")
            flash(f'Error sending reply: {str(e)}', 'error')
            
    except Exception as e:
        print(f"Fatal error in admin_reply: {str(e)}")
        flash(f'Error processing reply: {str(e)}', 'error')
        
    finally:
        if cursor:
            # Consume any unread results before closing
            while cursor.nextset():
                pass
            cursor.close()
        if connection:
            connection.close()
            
    return redirect(url_for('admin_messages'))

@app.route('/admin/settings')
@admin_required
def admin_settings():
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute('SELECT * FROM users WHERE is_admin = 1')
        users = cursor.fetchall()
        user = users[0] if users else {}

    except mysql.connector.Error as err:
        flash(f'Error fetching user data: {err}', 'error')
        user = {}

    finally:
        cursor.close()
        connection.close()

    return render_template('admin-settings.html', user=user)


# Admin login route
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        try:
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)
            
            # Check if user exists and is an admin
            cursor.execute('''
                SELECT * FROM users 
                WHERE email = %s AND is_admin = 1
                LIMIT 1
            ''', (email,))
            
            admin = cursor.fetchone()
            
            if admin and check_password_hash(admin['password'], password):
                # Store admin info in session
                session['admin_id'] = admin['user_id']
                session['admin_name'] = admin['name']
                session['admin_email'] = admin['email']
                session['is_admin'] = True
                
                flash('Welcome back, ' + admin['name'], 'success')
                return redirect(url_for('admin_dashboard'))
            else:
                flash('Invalid email, password, or unauthorized access.', 'error')
                return render_template('admin_login.html')
                
        except Error as e:
            flash('An error occurred. Please try again.', 'error')
            print(f"Database error: {e}")
            return render_template('admin_login.html')
        finally:
            cursor.close()
            connection.close()
    
    return render_template('admin_login.html')

# Admin logout route
@app.route('/admin/logout')
def admin_logout():
    # Remove admin session variables
    session.pop('admin_logged_in', None)
    session.pop('admin_id', None)
    session.pop('admin_name', None)
    session.pop('admin_email', None)
    session.pop('is_admin', None)  # Clear the is_admin flag as well
    
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('admin_login'))


# Logout Route
@app.route('/logout')
def logout():
    try:
        if current_user.is_authenticated:
            # Log the logout activity
            log_user_activity(current_user.id, 'LOGOUT', 'User logged out')
            
            # Clear the session
            logout_user()
            session.clear()
            
            flash('You have been successfully logged out.', 'success')
            
        return redirect(url_for('login'))
        
    except Exception as e:
        print(f"Error during logout: {e}")
        flash('An error occurred during logout.', 'error')
        return redirect(url_for('index'))

@app.route('/weekly-sales', methods=['GET'])
def get_weekly_sales():
    if 'loggedin' not in session:
        return jsonify({'error': 'Not logged in'}), 401
        
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        # Updated query to match your database schema
        cursor.execute("""
            SELECT 
                YEARWEEK(order_date) AS week,
                SUM(total_price) AS weekly_sales
            FROM orders 
            WHERE status = 'completed'
            AND buyer_id = %s
            AND order_date >= DATE_SUB(CURRENT_DATE, INTERVAL 12 WEEK)
            GROUP BY week
            ORDER BY week DESC
        """, (session['id'],))
        
        results = cursor.fetchall()
        
        if not results:
            return jsonify({
                "labels": [],
                "revenue": [],
                "current_week": 0,
                "previous_week": 0
            })

        # Extract current and previous week data
        current_week = float(results[0]['weekly_sales']) if results else 0
        previous_week = float(results[1]['weekly_sales']) if len(results) > 1 else 0

        # Format data for Chart.js
        sales_data = {
            "labels": [f"Week {row['week']}" for row in results][::-1],
            "revenue": [float(row['weekly_sales']) for row in results][::-1],
            "current_week": current_week,
            "previous_week": previous_week
        }
        
        return jsonify(sales_data)
        
    except Exception as e:
        print(f"Error fetching weekly sales: {str(e)}")
        return jsonify({
            'error': 'An error occurred while fetching sales data',
            'details': str(e)
        }), 500
        
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

# Add this debug route temporarily
@app.route('/debug_orders')
def debug_orders():
    if 'id' not in session:
        return {'error': 'Not logged in'}
        
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        # Check products for this seller
        cursor.execute('SELECT COUNT(*) as count FROM products WHERE seller_id = %s', (session['id'],))
        products_count = cursor.fetchone()['count']
        
        # Check orders
        cursor.execute('''
            SELECT COUNT(*) as count 
            FROM orders o 
            JOIN order_items oi ON o.order_id = oi.order_id 
            JOIN products p ON oi.product_id = p.product_id 
            WHERE p.seller_id = %s
        ''', (session['id'],))
        orders_count = cursor.fetchone()['count']
        
        # Get sample data
        cursor.execute('''
            SELECT 
                p.seller_id,
                p.name as product_name,
                o.status,
                o.order_id
            FROM products p
            LEFT JOIN order_items oi ON p.product_id = oi.product_id
            LEFT JOIN orders o ON oi.order_id = o.order_id
            WHERE p.seller_id = %s
            LIMIT 5
        ''', (session['id'],))
        sample_data = cursor.fetchall()
        
        return {
            'seller_id': session['id'],
            'products_count': products_count,
            'orders_count': orders_count,
            'sample_data': sample_data
        }
        
    finally:
        cursor.close()
        connection.close()

@app.route('/update_order_status', methods=['POST'])
def update_order_status():
    if 'id' not in session:
        return jsonify({'success': False, 'message': 'Please login first'})

    try:
        order_id = request.form.get('order_id')
        new_status = request.form.get('status')
        
        if not order_id or not new_status:
            return jsonify({'success': False, 'message': 'Missing required parameters'})

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Get order details including buyer information
        cursor.execute('''
            SELECT 
                o.*,
                u.user_id as buyer_id,
                u.name as buyer_name,
                u.email as buyer_email
            FROM orders o
            JOIN order_items oi ON o.order_id = oi.order_id
            JOIN products p ON oi.product_id = p.product_id
            JOIN users u ON o.buyer_id = u.user_id
            WHERE o.order_id = %s AND p.seller_id = %s
            LIMIT 1
        ''', (order_id, session['id']))
        
        order_data = cursor.fetchone()
        if not order_data:
            return jsonify({'success': False, 'message': 'Order not found or access denied'})

        # Update order status
        cursor.execute('''
            UPDATE orders 
            SET status = %s 
            WHERE order_id = %s
        ''', (new_status, order_id))

        # Create notification for the buyer
        status_messages = {
            'pending': 'Your order is now pending processing.',
            'processing': 'Your order is now being processed.',
            'shipped': 'Good news! Your order has been shipped.',
            'completed': 'Your order has been completed. Thank you for shopping!',
            'cancelled': 'Your order has been cancelled by the seller.',
            'return': 'Your return request has been received.'
        }
        
        notification_message = status_messages.get(new_status, f'Your order status has been updated to: {new_status}')
        
        # Insert notification
        cursor.execute('''
            INSERT INTO notifications 
                (user_id, message, type, order_id, created_at, is_read) 
            VALUES 
                (%s, %s, %s, %s, NOW(), 0)
        ''', (
            order_data['buyer_id'],
            notification_message,
            'order_status',
            order_id
        ))

        connection.commit()
        
        # Send email notification
        try:
            send_email(
                to_email=order_data['buyer_email'],
                subject=f'Order #{order_id} Status Update',
                body=f'''
                    Dear {order_data['buyer_name']},

                    {notification_message}

                    Order Details:
                    - Order ID: #{order_id}
                    - New Status: {new_status}
                    - Updated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

                    You can check your order details in your account dashboard.

                    Best regards,
                    Your Lithub Team
                '''
            )
        except Exception as email_error:
            print(f"Email sending failed: {str(email_error)}")
            # Continue execution even if email fails
        
        response_data = {
            'success': True,
            'message': f'Order status updated to {new_status}',
            'order_id': order_id,
            'new_status': new_status
        }
        
        return jsonify(response_data)

    except mysql.connector.Error as e:
        print(f"Database error: {str(e)}")
        return jsonify({'success': False, 'message': 'A database error occurred'}), 500
        
    except Exception as e:
        print(f"Error updating order status: {str(e)}")
        return jsonify({'success': False, 'message': 'An unexpected error occurred'}), 500
        
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection.is_connected():
            connection.close()

@app.route('/view_order_details/<int:order_id>')
def view_order_details(order_id):
    if 'id' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('login'))

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Get user data
        cursor.execute('SELECT * FROM users WHERE user_id = %s', (session['id'],))
        user = cursor.fetchone()
        
        if not user:
            flash('User not found', 'error')
            return redirect(url_for('login'))
            
        # Get order details
        cursor.execute('''
            SELECT o.order_id, o.buyer_id, o.order_date, o.status, o.total_price, o.shipping_address, o.payment_method, o.completed_at, u.name as buyer_name, u.email as buyer_email
            FROM orders o
            JOIN users u ON o.buyer_id = u.user_id
            WHERE o.order_id = %s AND o.buyer_id = %s
        ''', (order_id, session['id']))
        
        order_data = cursor.fetchone()
        
        if not order_data:
            flash('Order not found or unauthorized', 'error')
            return redirect(url_for('user_purchase'))
            
        # Convert order data to a regular dictionary
        order = dict(order_data)
        
        # Get order items
        cursor.execute('''
            SELECT oi.order_item_id, oi.product_id, oi.quantity, oi.price, p.name as product_name, p.author, p.image, p.product_id
            FROM order_items oi
            JOIN products p ON oi.product_id = p.product_id
            WHERE oi.order_id = %s
        ''', (order_id,))
        
        # Convert items to list of dictionaries
        items = [dict(item) for item in cursor.fetchall()]
        order['items'] = items
        
        print("Order data:", order)  # Debug print
        print("Items:", items)  # Debug print
        
        return render_template('order-details.html', 
                             order=order,
                             user=user)  # Pass user to template
        
    except Exception as e:
        print(f"Error fetching order details: {str(e)}")
        print(f"Session ID: {session['id']}")
        print(f"Order ID: {order_id}")
        flash('Error fetching order details', 'error')
        return redirect(url_for('user_purchase'))
        
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

@app.route('/admin/seller-report/<int:user_id>')
def admin_seller_report(user_id):
    print(f"Accessing seller report for user_id: {user_id}")  # Debug log
    
    if 'id' not in session:
        print("No session ID found")  # Debug log
        return jsonify({'error': 'Not logged in'}), 401
        
    if not session.get('is_admin'):
        print("User is not admin")  # Debug log
        return jsonify({'error': 'Not authorized'}), 403
        
    connection = None
    cursor = None
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Verify seller exists
        cursor.execute('SELECT user_id, name FROM users WHERE user_id = %s', (user_id,))
        seller = cursor.fetchone()
        
        if not seller:
            print(f"No seller found with ID: {user_id}")  # Debug log
            return jsonify({'error': 'Seller not found'}), 404
            
        print(f"Found seller: {seller}")  # Debug log
        
        # Get today's stats
        cursor.execute('''
            SELECT 
                COUNT(DISTINCT o.order_id) as today_orders,
                COALESCE(SUM(o.total_price), 0) as today_sales
            FROM orders o
            JOIN order_items oi ON o.order_id = oi.order_id
            JOIN products p ON oi.product_id = p.product_id
            WHERE p.seller_id = %s
            AND DATE(o.order_date) = CURDATE()
        ''', (user_id,))
        
        today_stats = cursor.fetchone()
        print(f"Today's stats: {today_stats}")  # Debug log
        
        # Get monthly stats
        cursor.execute('''
            SELECT 
                COUNT(DISTINCT o.order_id) as monthly_orders,
                COALESCE(SUM(o.total_price), 0) as monthly_revenue
            FROM orders o
            JOIN order_items oi ON o.order_id = oi.order_id
            JOIN products p ON oi.product_id = p.product_id
            WHERE p.seller_id = %s
            AND MONTH(o.order_date) = MONTH(CURRENT_DATE())
            AND YEAR(o.order_date) = YEAR(CURRENT_DATE())
        ''', (user_id,))
        
        monthly_stats = cursor.fetchone()
        print(f"Monthly stats: {monthly_stats}")  # Debug log
        
        # Get total customers
        cursor.execute('''
            SELECT COUNT(DISTINCT o.buyer_id) as total_customers
            FROM orders o
            JOIN order_items oi ON o.order_id = oi.order_id
            JOIN products p ON oi.product_id = p.product_id
            WHERE p.seller_id = %s
        ''', (user_id,))
        
        customer_stats = cursor.fetchone()
        print(f"Customer stats: {customer_stats}")  # Debug log
        
        response_data = {
            'seller_name': seller['name'],
            'today_sales': float(today_stats['today_sales']) if today_stats['today_sales'] else 0,
            'today_orders': today_stats['today_orders'],
            'monthly_revenue': float(monthly_stats['monthly_revenue']) if monthly_stats['monthly_revenue'] else 0,
            'monthly_orders': monthly_stats['monthly_orders'],
            'total_customers': customer_stats['total_customers']
        }
        
        print(f"Sending response: {response_data}")  # Debug log
        return jsonify(response_data)
        
    except Exception as e:
        print(f"Error in seller report: {str(e)}")
        print(f"Error type: {type(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500
        
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route('/search')
def search():
    query = request.args.get('q', '')
    if not query:
        return jsonify([])
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Search across all product types
        cursor.execute('SELECT * FROM products WHERE name LIKE %s OR description LIKE %s', (f'%{query}%', f'%{query}%'))
        results = cursor.fetchall()
        return jsonify(results)
        
    except Exception as e:
        print(f"Search error: {str(e)}")
        return jsonify([])
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route('/search-results')
def search_results():
    query = request.args.get('q', '')
    if not query:
        return redirect(url_for('index'))
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute('SELECT * FROM products WHERE name LIKE %s OR description LIKE %s', (f'%{query}%', f'%{query}%'))
        products = cursor.fetchall()
        
        return render_template('search-results.html', 
                             products=products, 
                             query=query,
                             user=get_user_data())  # Add this line
        
    except Exception as e:
        print(f"Search error: {str(e)}")  # Add debugging
        flash(f"An error occurred: {str(e)}", "error")
        return redirect(url_for('index'))
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def save_rating(data):
    connection = None
    cursor = None
    try:
        # Extract data
        product_id = data['productId']
        buyer_id = data['buyerId']
        product_quality = data['productQuality']
        seller_service = data['sellerService']
        delivery_service = data['deliveryService']
        quality_comment = data['qualityComment']
        service_comment = data['serviceComment']
        delivery_comment = data['deliveryComment']

        # Create a database connection
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        if 'productId' not in data or 'buyerId' not in data:
            return False

        # Check if the product_id exists in the products table
        check_product_query = "SELECT COUNT(*) FROM products WHERE product_id = %s"
        cursor.execute(check_product_query, (product_id,))
        product_exists = cursor.fetchone()['COUNT(*)']

        if product_exists == 0:
            print(f"Product ID {product_id} does not exist.")
            return False

        # Check if the buyer_id exists in the users table
        check_buyer_query = "SELECT COUNT(*) FROM users WHERE user_id = %s"
        cursor.execute(check_buyer_query, (buyer_id,))
        buyer_exists = cursor.fetchone()['COUNT(*)']

        if buyer_exists == 0:
            print(f"Buyer ID {buyer_id} does not exist.")
            return False

        # Insert the review into the database
        insert_query = """
        INSERT INTO reviews (product_id, buyer_id, product_quality, seller_service, delivery_service, 
                           quality_comment, service_comment, delivery_comment)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (
            product_id, buyer_id, product_quality, seller_service, delivery_service,
            quality_comment, service_comment, delivery_comment
        ))
        connection.commit()
        print("Rating saved successfully")
        return True

    except Exception as e:
        print(f"Error while saving rating: {str(e)}")
        if connection:
            connection.rollback()
        return False

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route('/submit_rating', methods=['POST'])
def submit_rating():
    cursor = None  # Initialize cursor to None
    connection = None  # Initialize connection to None
    try:
        data = request.get_json()
        print("Received data:", data)  # Log the incoming data
        
        # Enhanced validation
        required_fields = [
            'product_id', 
            'buyer_id', 
            'product_quality_rating', 
            'seller_service_rating', 
            'delivery_service_rating'
        ]
        if not data or not all(field in data for field in required_fields):
            print("Missing required fields")  # Log missing fields
            return jsonify({'success': False, 'message': 'Missing required fields'}), 400
        
        # Validate rating values
        if not all(1 <= data[field] <= 5 for field in ['product_quality_rating', 'seller_service_rating', 'delivery_service_rating']):
            print("Invalid rating values")  # Log invalid values
            return jsonify({
                'success': False,
                'message': 'Rating values must be between 1 and 5'
            }), 400

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Check for existing review
        cursor.execute('''
            SELECT review_id 
            FROM reviews 
            WHERE product_id = %s AND buyer_id = %s
        ''', (data['product_id'], data['buyer_id']))
        
        existing_review = cursor.fetchone()
        if existing_review:
            print("Review already exists")  # Log existing review
            return jsonify({
                'success': False,
                'message': 'You have already rated this product'
            }), 400

        # Insert the review
        insert_query = '''
            INSERT INTO reviews (
                product_id, buyer_id, product_quality, seller_service, delivery_service, 
                quality_comment, service_comment, delivery_comment
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        '''
        
        values = (
            data['product_id'],
            data['buyer_id'],
            data['product_quality_rating'],
            data['seller_service_rating'],
            data['delivery_service_rating'],
            data.get('product_quality_comment', ''),
            data.get('seller_service_comment', ''),
            data.get('delivery_service_comment', '')
        )
        
        cursor.execute(insert_query, values)
        connection.commit()

        # Update the order_items table to set is_rated to 1
        try:
            print(f"Updating order_items: product_id={data['product_id']}, order_id={data['order_id']}")
            
            cursor.execute('''
                SELECT * FROM order_items 
                WHERE product_id = %s AND order_id = %s
            ''', (data['product_id'], data['order_id']))
            
            existing_record = cursor.fetchone()
            if existing_record:
                cursor.execute('''
                    UPDATE order_items 
                    SET is_rated = 1 
                    WHERE product_id = %s AND order_id = %s
                ''', (data['product_id'], data['order_id']))
                connection.commit()
                print("Update successful.")
            else:
                print("No matching record found.")
        except Exception as e:
            print(f"Error updating order_items: {str(e)}")
            connection.rollback()

        connection.commit()
        
        return jsonify({
            'success': True,
            'message': 'Rating submitted successfully'
        })
        
    except Exception as e:
        print(f"Error while saving rating: {e}")
        if connection:
            connection.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to save rating: {str(e)}'
        }), 500
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()

@app.route('/check_rating', methods=['POST'])
def check_rating():
    try:
        data = request.get_json()
        product_id = data.get('product_id')
        buyer_id = data.get('buyer_id')

        if not product_id or not buyer_id:
            return jsonify({'success': False, 'message': 'Missing required parameters'}), 400

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Check if a rating exists
        cursor.execute('''
            SELECT review_id 
            FROM reviews 
            WHERE product_id = %s AND buyer_id = %s
        ''', (product_id, buyer_id))
        
        result = cursor.fetchone()
        
        cursor.close()
        connection.close()

        return jsonify({
            'success': True,
            'is_rated': bool(result)
        })

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/get_sales_data', methods=['GET'])
def get_sales_data():
    if 'loggedin' not in session or not session.get('is_admin', False):
        return jsonify({'error': 'Unauthorized'}), 401

    from_date = request.args.get('from')
    to_date = request.args.get('to')
    
    # Validate date parameters
    if not from_date or not to_date:
        to_date = datetime.now().strftime('%Y-%m-%d')
        from_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    # Ensure the dates are in the correct format
    try:
        datetime.strptime(from_date, '%Y-%m-%d')
        datetime.strptime(to_date, '%Y-%m-%d')
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD.'}), 400

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        # Get sales data for the date range
        cursor.execute('''
            SELECT 
                DATE(order_date) as date,
                COALESCE(SUM(total_price), 0) as daily_sales
            FROM orders
            WHERE DATE(order_date) BETWEEN %s AND %s
            GROUP BY DATE(order_date)
            ORDER BY date
        ''', (from_date, to_date))
        
        sales_data = cursor.fetchall()
        
        # Get overall stats
        cursor.execute('''
            SELECT 
                COALESCE(SUM(total_price), 0) as revenue,
                COALESCE(SUM(total_price * 0.05), 0) as commission,
                COUNT(*) as total_orders
            FROM orders
            WHERE DATE(order_date) BETWEEN %s AND %s
        ''', (from_date, to_date))
        
        stats = cursor.fetchone()
        
        # If stats is None, set default values
        if stats is None:
            stats = {'revenue': 0, 'commission': 0, 'total_orders': 0}
        
        # Get top products
        cursor.execute('''
            SELECT 
                p.name,
                p.price,
                p.image,
                COUNT(*) as order_count
            FROM products p
            JOIN order_items oi ON p.product_id = oi.product_id
            JOIN orders o ON oi.order_id = o.order_id
            WHERE DATE(o.order_date) BETWEEN %s AND %s
            GROUP BY p.product_id, p.name, p.price, p.image
            ORDER BY order_count DESC
            LIMIT 5
        ''', (from_date, to_date))
        
        top_products = cursor.fetchall() or []
        
        # Calculate growth rate
        cursor.execute('''
            SELECT COUNT(*) as repeat_orders
            FROM (
                SELECT buyer_id
                FROM orders
                WHERE DATE(order_date) BETWEEN %s AND %s
                GROUP BY buyer_id
                HAVING COUNT(*) > 1
            ) as repeat_customers
        ''', (from_date, to_date))
        
        repeat_orders_result = cursor.fetchone()
        repeat_orders = repeat_orders_result['repeat_orders'] if repeat_orders_result else 0
        
        total_orders = stats['total_orders']
        growth_rate = (repeat_orders / total_orders * 100) if total_orders > 0 else 0
        
        # Prepare response
        response_data = {
            'labels': [row['date'].strftime('%Y-%m-%d') for row in sales_data],
            'sales': [float(row['daily_sales']) for row in sales_data],
            'stats': {
                'revenue': float(stats['revenue']),
                'commission': float(stats['commission']),
                'orders': stats['total_orders'],
                'growth_rate': round(growth_rate, 2),
                'top_products': [{
                    'name': product['name'],
                    'price': float(product['price']),
                    'image_path': url_for('static', filename=f'images/{product["image"]}') if product['image'] else url_for('static', filename='images/default_image.jpg'),
                    'order_count': product['order_count']
                } for product in top_products]
            }
        }
        
        # Log the response data for debugging
        print("Response Data:", response_data)
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"Error fetching sales data: {e}")
        return jsonify({'error': str(e)}), 500
        
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def log_user_activity(user_id, action, description, ip_address=None):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        if ip_address is None:
            ip_address = request.remote_addr
            
        cursor.execute('''
            INSERT INTO user_logs (user_id, action, description, ip_address, timestamp)
            VALUES (%s, %s, %s, %s, NOW())
        ''', (user_id, action, description, ip_address))
        
        connection.commit()
        
    except Exception as e:
        print(f"Error logging user activity: {e}")
    finally:
        if cursor:
            cursor.close()
        if 'connection' in locals():
            connection.close()

@app.route('/admin/user-logs')
@admin_required
def admin_user_logs():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        # Get filter parameters
        user_id = request.args.get('user_id', '')
        activity_type = request.args.get('activity_type', '')
        from_date = request.args.get('from_date', '')
        to_date = request.args.get('to_date', '')
        
        # Base query with proper JOIN to get user details
        query = '''
            SELECT 
                l.*,
                u.name as user_name,
                u.email as user_email,
                l.timestamp,
                l.action,
                l.description,
                l.ip_address
            FROM user_logs l
            JOIN users u ON l.user_id = u.user_id
            WHERE 1=1
        '''
        params = []
        
        # Add filters only if they are provided
        if user_id:
            query += " AND l.user_id = %s"
            params.append(user_id)
        
        if activity_type:
            query += " AND l.action = %s"
            params.append(activity_type)
        
        if from_date:
            query += " AND DATE(l.timestamp) >= %s"
            params.append(from_date)
        
        if to_date:
            query += " AND DATE(l.timestamp) <= %s"
            params.append(to_date)
        
        query += " ORDER BY l.timestamp DESC"
        
        # Get logs
        cursor.execute(query, params)
        logs = cursor.fetchall()
        
        # Get all users for filter dropdown
        cursor.execute('SELECT user_id, name, email FROM users ORDER BY name')
        users = cursor.fetchall()
        
        # Get unique activity types for filter dropdown
        cursor.execute('SELECT DISTINCT action FROM user_logs ORDER BY action')
        activity_types = [row['action'] for row in cursor.fetchall()]

        return render_template('admin-user-logs.html',
                             logs=logs,
                             users=users,
                             activity_types=activity_types,
                             selected_user_id=user_id,
                             selected_activity_type=activity_type,
                             from_date=from_date,
                             to_date=to_date)
                             
    except Exception as e:
        print(f"Error in admin_user_logs: {e}")
        flash('An error occurred while loading user logs', 'error')
        return redirect(url_for('admin_dashboard'))
        
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route('/send_contact_message', methods=['POST'])
def send_contact_message():
    if 'id' not in session:
        print("DEBUG: User not logged in")
        return jsonify({'error': 'Not logged in'})
    
    connection = None
    cursor = None
    try:
        data = request.get_json()
        message = data.get('message')
        reply_to = data.get('reply_to')
        
        if not message:
            return jsonify({'error': 'Message is required'})
            
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Database connection failed'})
            
        cursor = connection.cursor(dictionary=True)
        
        # Get admin user ID and sender name
        cursor.execute('''
            SELECT u1.user_id as admin_id, u2.name as sender_name 
            FROM users u1, users u2 
            WHERE u1.is_admin=1 AND u2.user_id=%s
        ''', (session['id'],))
        
        result = cursor.fetchone()
        
        if not result:
            return jsonify({'error': 'Could not find admin or sender info'})
            
        admin_id = result['admin_id']
        sender_name = result['sender_name']
        
        # If replying to a message, get original sender as receiver
        receiver_id = admin_id
        if reply_to:
            cursor.execute('SELECT sender_id FROM chat_messages WHERE message_id = %s', (reply_to,))
            original = cursor.fetchone()
            if original:
                receiver_id = original['sender_id']
        
        # Insert into chat_messages table with reply_to field
        cursor.execute('''
            INSERT INTO chat_messages 
            (sender_id, receiver_id, message, status, is_admin_reply, is_reply) 
            VALUES (%s, %s, %s, 'unread', TRUE, TRUE)
        ''', (session['id'], receiver_id, message))
        new_message_id = cursor.lastrowid
        
        # Create message status entry
        cursor.execute('''
            INSERT INTO chat_message_status 
            (message_id, user_id, is_read) 
            VALUES (%s, %s, FALSE)
        ''', (new_message_id, receiver_id))
        
        connection.commit()
        return jsonify({
            'success': True,
            'message': {
                'message_id': new_message_id,
                'sender_id': session['id'],
                'receiver_id': receiver_id,
                'message': message,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'is_admin_reply': False,
                'sender_name': sender_name,
                'reply_to_message_id': reply_to
            }
        })
        
    except Exception as e:
        print(f"DEBUG: Error in send_contact_message: {str(e)}")
        if connection:
            connection.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        })
    finally:
        if cursor:
            cursor.fetchall()  # Consume any unread results
            cursor.close()
        if connection:
            connection.close()
            
@app.route('/delete_message', methods=['POST'])
def delete_message():
    if 'id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
        
    try:
        data = request.get_json()
        message_type = data.get('message_type')
        message_id = data.get('message_id')
        
        if not message_type or not message_id:
            return jsonify({'error': 'Message type and ID are required'})
            
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Verify message ownership
        if message_type == 'contact':
            cursor.execute('''
                SELECT user_id FROM contact_messages 
                WHERE message_id = %s
            ''', (message_id,))
        else:  # chat
            cursor.execute('''
                SELECT sender_id as user_id FROM chat_messages 
                WHERE message_id = %s
            ''', (message_id,))
            
        message = cursor.fetchone()
        if not message or message['user_id'] != session['id']:
            return jsonify({'error': 'Message not found or unauthorized'})
        
        # Delete the message and any associated replies
        if message_type == 'contact':
            cursor.execute('DELETE FROM admin_replies WHERE message_id = %s', (message_id,))
            cursor.execute('DELETE FROM contact_messages WHERE message_id = %s', (message_id,))
        else:  # chat
            cursor.execute('DELETE FROM chat_messages WHERE message_id = %s', (message_id,))
            
        connection.commit()
        
        return jsonify({'success': True})
        
    except Exception as e:
        print(f"Error in delete_message: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        })
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

@app.route('/get_messages')
def get_messages():
    if 'loggedin' not in session:
        flash('Please log in to view your profile.', 'error')
        return redirect(url_for('login'))
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT DISTINCT 
                u.user_id as conversation_with,
                u.name as display_name,
                (
                    SELECT message 
                    FROM chat_messages 
                    WHERE (sender_id = %s AND receiver_id = u.user_id)
                    OR (sender_id = u.user_id AND receiver_id = %s)
                    ORDER BY timestamp DESC 
                    LIMIT 1
                ) as last_message,
                (
                    SELECT COUNT(*)
                    FROM chat_messages
                    WHERE receiver_id = %s 
                    AND status = 'unread'
                ) as unread_count
            FROM users u
            WHERE u.user_id IN (
                SELECT DISTINCT 
                    CASE 
                        WHEN sender_id = %s THEN receiver_id
                        ELSE sender_id
                    END
                FROM chat_messages
                WHERE sender_id = %s OR receiver_id = %s
            )
        """, (session['id'], session['id'], session['id'], session['id'], session['id'], session['id']))
        
        conversations = cursor.fetchall()
        return jsonify(conversations)
        
    except Exception as e:
        print(f"Error in get_messages: {str(e)}")
        return jsonify({'error': str(e)}), 500
        
    finally:
        if connection:
            connection.close()

@app.route('/get_chat_messages/<int:other_user_id>')
def chat_messages(other_user_id):
    if 'loggedin' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Get messages between current user and other user
        cursor.execute("""
            SELECT m.*, u.name as sender_name,
                u.is_admin as sender_is_admin,
                u.is_seller as sender_is_seller,
                CASE WHEN m.sender_id = %s THEN 'sent' ELSE 'received' END as message_type
            FROM chat_messages m
            JOIN users u ON m.sender_id = u.user_id
            WHERE (m.sender_id = %s AND m.receiver_id = %s)
            OR (m.sender_id = %s AND m.receiver_id = %s)
            ORDER BY m.timestamp ASC
        """, (session['id'], session['id'], other_user_id, other_user_id, session['id']))
        
        messages = cursor.fetchall()
        
        # Format timestamps
        for msg in messages:
            if msg['timestamp']:
                msg['timestamp'] = msg['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
        
        # Mark messages as read
        cursor.execute("""
            UPDATE chat_messages 
            SET status = 'read'
            WHERE receiver_id = %s AND sender_id = %s AND status = 'unread'
        """, (session['id'], other_user_id))
        
        connection.commit()
        return jsonify(messages)
        
    except Exception as e:
        print(f"Error in chat_messages: {str(e)}")
        return jsonify({'error': str(e)}), 500
    finally:
        if connection:
            connection.close()

@app.route('/send_message', methods=['POST'])
def send_message():
    if 'loggedin' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    data = request.get_json()
    receiver_id = data.get('receiver_id')
    message = data.get('message')
    
    if not receiver_id or not message:
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute("""
            INSERT INTO chat_messages (sender_id, receiver_id, message, timestamp, status)
            VALUES (%s, %s, %s, NOW(), 'unread')
        """, (session['id'], receiver_id, message))
        
        # Get the sent message details
        cursor.execute("""
            SELECT m.*, u.name as sender_name,
                u.is_admin as sender_is_admin,
                u.is_seller as sender_is_seller,
                'sent' as message_type
            FROM chat_messages m
            JOIN users u ON m.sender_id = u.user_id
            WHERE m.message_id = LAST_INSERT_ID()
        """)
        
        sent_message = cursor.fetchone()
        if sent_message and sent_message['timestamp']:
            sent_message['timestamp'] = sent_message['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
        
        connection.commit()
        return jsonify(sent_message)
        
    except Exception as e:
        print(f"Error sending message: {str(e)}")
        return jsonify({'error': str(e)}), 500
    finally:
        if connection:
            connection.close()
            

def create_notification(user_id, message, notification_type=None, order_id=None):
    connection = None
    cursor = None
    try:
        print(f"Debug - Starting notification creation for user_id: {user_id}")
        print(f"Debug - Message: {message}")
        print(f"Debug - Type: {notification_type}")
        print(f"Debug - Order ID: {order_id}")
        
        # Check if notifications table exists
        cursor.execute('''
            SELECT COUNT(*)
            FROM information_schema.tables 
            WHERE table_schema = DATABASE()
            AND table_name = 'notifications'
        ''')
        table_exists = cursor.fetchone()['COUNT(*)'] > 0
        print(f"Debug - Notifications table exists: {table_exists}")# Check for existing welcome notification
        cursor.execute('''
            SELECT COUNT(*) as count 
            FROM notifications 
            WHERE user_id = %s AND type = 'welcome'
            ''', (session['id'],))
        has_welcome = cursor.fetchone()['count'] > 0

# Create welcome notification only if user doesn't have one
        if not has_welcome:
            print("Debug - Creating welcome notification")
            create_notification(
                user_id=session['id'],
                message="Welcome to LitHub! This is your notification center.",
                notification_type="welcome"
            )
        
        if not table_exists:
            print("Debug - Creating notifications table")
            cursor.execute('''
                CREATE TABLE notifications (
                    notification_id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    message TEXT NOT NULL,
                    type VARCHAR(50),
                    order_id INT,
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    is_read TINYINT(1) DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
                ) ENGINE=InnoDB
            ''')
            connection.commit()
            print("Debug - Created new notifications table")
        
        # Insert notification with explicit timestamp
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"Debug - Inserting notification at {current_time}")
        
        insert_query = '''
            INSERT INTO notifications (user_id, message, type, order_id, created_at, is_read)
            VALUES (%s, %s, %s, %s, %s, 0)
        '''
        insert_values = (int(user_id), message, notification_type, order_id, current_time)
        
        cursor.execute(insert_query, insert_values)
        connection.commit()
        
        # Verify insertion
        cursor.execute('SELECT LAST_INSERT_ID() as id')
        result = cursor.fetchone()
        notification_id = result['id']
        print(f"Debug - Created notification with ID: {notification_id}")
        
        # Double check the notification exists
        cursor.execute('''
            SELECT * FROM notifications 
            WHERE notification_id = %s
        ''', (notification_id,))
        notification = cursor.fetchone()
        print(f"Debug - Verification - Created notification: {notification}")
        
        # Check all notifications for this user
        cursor.execute('SELECT COUNT(*) as count FROM notifications WHERE user_id = %s', (user_id,))
        count = cursor.fetchone()['count']
        print(f"Debug - Total notifications for user {user_id}: {count}")
        
        return True
        
    except Exception as e:
        print(f"Error in create_notification: {str(e)}")
        print(f"Error type: {type(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        if connection:
            connection.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

@app.route('/delete_notification/<int:notification_id>', methods=['POST'])
def delete_notification(notification_id):
    if 'loggedin' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Verify the notification belongs to the current user
        cursor.execute('''
            SELECT user_id 
            FROM notifications 
            WHERE notification_id = %s
        ''', (notification_id,))
        notification = cursor.fetchone()
        
        if not notification or notification['user_id'] != session['id']:
            return jsonify({'success': False, 'message': 'Notification not found or unauthorized'}), 403
        
        # Delete the notification
        cursor.execute('''
            DELETE FROM notifications 
            WHERE notification_id = %s AND user_id = %s
        ''', (notification_id, session['id']))
        
        connection.commit()
        return jsonify({'success': True, 'message': 'Notification deleted successfully'})
        
    except Exception as e:
        print(f"Error deleting notification: {str(e)}")
        return jsonify({'success': False, 'message': 'Error deleting notification'}), 500
        
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

@app.route('/buy_again/<int:order_id>')
def buy_again(order_id):
    if 'id' not in session:
        return jsonify({'error': 'Please login first'}), 401

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Get order items
        cursor.execute('''
            SELECT 
                oi.product_id,
                oi.quantity,
                p.quantity as available_quantity
            FROM order_items oi
            JOIN products p ON oi.product_id = p.product_id
            WHERE oi.order_id = %s
        ''', (order_id,))
        
        items = cursor.fetchall()
        
        if not items:
            flash('Order items not found', 'error')
            return redirect(url_for('user_purchase'))

        # Clear existing cart first
        cursor.execute('DELETE FROM cart WHERE user_id = %s', (session['id'],))

        # Add items to cart
        for item in items:
            # Check stock availability
            if item['quantity'] > item['available_quantity']:
                flash(f'Not enough stock available for some items. Added maximum available quantity.', 'warning')
                quantity = item['available_quantity']
            else:
                quantity = item['quantity']

            cursor.execute('''
                INSERT INTO cart (user_id, product_id, quantity)
                VALUES (%s, %s, %s)
            ''', (session['id'], item['product_id'], quantity))

        connection.commit()
        return redirect(url_for('checkout'))

    except Exception as e:
        print(f"Error in buy_again: {str(e)}")
        flash('Error processing your request', 'error')
        return redirect(url_for('user_purchase'))
        
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route('/get_unread_count')
def get_unread_count():
    if 'id' not in session:
        return jsonify({
            'notification_count': 0,
            'message_count': 0
        })
        
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Get unread notifications count
        cursor.execute('''
            SELECT COUNT(*) as count 
            FROM notifications 
            WHERE user_id = %s AND is_read = 0
        ''', (session['id'],))
        notification_result = cursor.fetchone()
        
        # Get unread messages count
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM chat_messages
            WHERE receiver_id = %s 
            AND status = 'unread'
        """, (session['id'],))
        message_result = cursor.fetchone()
        
        return jsonify({
            'notification_count': notification_result['count'] if notification_result else 0,
            'message_count': message_result['count'] if message_result else 0
        })
        
    except Exception as e:
        print(f"Error getting unread counts: {str(e)}")
        return jsonify({
            'notification_count': 0,
            'message_count': 0,
            'error': str(e)
        }), 500
        
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route('/contact_seller/<int:order_id>')
def contact_seller(order_id):
    if 'id' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('login'))

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Get seller information from the order
        cursor.execute('''
            SELECT DISTINCT
                o.order_id,
                u.user_id as seller_id,
                u.name as seller_name,
                p.name as product_name
            FROM orders o
            JOIN order_items oi ON o.order_id = oi.order_id
            JOIN products p ON oi.product_id = p.product_id
            JOIN users u ON p.seller_id = u.user_id
            WHERE o.order_id = %s AND o.buyer_id = %s
            LIMIT 1
        ''', (order_id, session['id']))
        
        seller_info = cursor.fetchone()
        
        if not seller_info:
            return jsonify({
                'success': False,
                'message': 'Seller information not found'
            }), 404
            
        # Create initial message about the order inquiry
        message = f"Inquiry about Order #{order_id} - {seller_info['product_name']}"
        cursor.execute('''
            INSERT INTO chat_messages 
            (sender_id, receiver_id, message, status, timestamp)
            VALUES (%s, %s, %s, 'unread', NOW())
        ''', (session['id'], seller_info['seller_id'], message))
        
        connection.commit()
        
        # Return seller info for the chat modal
        return jsonify({
            'success': True,
            'seller': {
                'id': seller_info['seller_id'],
                'name': seller_info['seller_name']
            }
        })
        
    except Exception as e:
        print(f"Error in contact_seller: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Error contacting seller. Please try again.'
        }), 500
        
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route('/get_user_name/<int:user_id>')
@login_required
def get_user_name(user_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute("SELECT username FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        
        if user:
            return jsonify({'name': user['username']})
        return jsonify({'name': 'Unknown User'}), 404
        
    except Exception as e:
        print(f"Error in get_user_name: {str(e)}")
        return jsonify({'name': 'Unknown User'}), 500
        
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
        
@app.route('/mark_messages_read/<int:other_user_id>', methods=['POST'])
def mark_messages_read(other_user_id):
    if 'id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
        
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute('''
            UPDATE chat_messages 
            SET status = 'read'
            WHERE sender_id = %s AND receiver_id = %s AND status = 'unread'
        ''', (other_user_id, session['id']))
        
        connection.commit()
        return jsonify({'success': True})
        
    except Exception as e:
        print(f"Error marking messages as read: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500
        
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route('/admin/seller-request/<action>/<int:request_id>', methods=['POST'])
def handle_seller_request(action, request_id):
    if 'loggedin' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Unauthorized'}), 403
        
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Get the user_id and current status from seller_requests
        cursor.execute('''
            SELECT sr.user_id, sr.status, u.email 
            FROM seller_requests sr
            JOIN users u ON sr.user_id = u.user_id 
            WHERE sr.request_id = %s
        ''', (request_id,))
        request_data = cursor.fetchone()
        
        if not request_data:
            return jsonify({'error': 'Seller request not found'}), 404
            
        if request_data['status'] != 'pending':
            return jsonify({'error': 'Request has already been processed'}), 400
            
        if action == 'approve':
            # Update user to seller status
            cursor.execute('UPDATE users SET is_seller = TRUE WHERE user_id = %s', 
                         (request_data['user_id'],))
            
            # Update request status
            cursor.execute('UPDATE seller_requests SET status = "approved" WHERE request_id = %s', 
                         (request_id,))
            
            # Add notification
            notification_message = "Your seller registration has been approved! You can now start selling."
            notification_type = "seller_approval"
            
        elif action == 'reject':
            # Get rejection reason from request
            rejection_data = request.get_json()
            reason = rejection_data.get('reason', 'No reason provided')
            
            # Update request status
            cursor.execute('''
                UPDATE seller_requests 
                SET status = "rejected", rejection_reason = %s 
                WHERE request_id = %s
            ''', (reason, request_id))
            
            # Add notification
            notification_message = f"Your seller registration was rejected. Reason: {reason}"
            notification_type = "seller_rejection"
            
        else:
            return jsonify({'error': 'Invalid action'}), 400
            
        # Insert notification
        cursor.execute('''
            INSERT INTO notifications 
            (user_id, message, type, created_at) 
            VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
        ''', (request_data['user_id'], notification_message, notification_type))
        
        connection.commit()
        
        return jsonify({
            'message': f'Seller request {action}ed successfully',
            'status': action + 'ed'
        })
        
    except Exception as e:
        print(f"Error in handle_seller_request: {str(e)}")
        connection.rollback()
        return jsonify({'error': str(e)}), 500
        
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

@app.route('/admin/get_print_data')
@admin_required
def get_print_data():
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Get sales data for the date range
        cursor.execute('''
            SELECT 
                DATE(o.order_date) as date,
                p.name,
                oi.quantity,
                oi.price,
                (oi.price * oi.quantity) as total_price
            FROM orders o
            JOIN order_items oi ON o.order_id = oi.order_id
            JOIN products p ON oi.product_id = p.product_id
            WHERE o.status != 'canceled'
            ORDER BY o.order_date DESC
        ''')
        
        sales = cursor.fetchall()
        
        return jsonify({
            'sales': sales,
            'current_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        
    except Exception as e:
        print(f"Error getting print data: {str(e)}")
        return jsonify({'error': 'Failed to get print data'}), 500
        
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

#backend for mobile

@app.route('/api/login', methods=['POST'])
@cross_origin()
def api_login():
    email = request.json.get('email')
    password = request.json.get('password')
    
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
    user = cursor.fetchone()
    
    if user and check_password_hash(user['password'], password):
        access_token = create_access_token(identity=str(user['user_id']))
        return jsonify({'access_token': access_token, 'user': {
            'user_id': user['user_id'],
            'name': user['name'],
            'email': user['email']
        }}), 200
    
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/products', methods=['GET'])
@cross_origin()
def get_products():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    cursor.close()
    connection.close()
    return jsonify(products)


@app.route('/api/product/<int:product_id>', methods=['GET'])
@cross_origin()
@jwt_required()
def get_product_details(product_id):
    user_id = get_jwt_identity()
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute('''
            SELECT 
                p.product_id,
                p.name,
                p.price,
                p.image,
                p.quantity,
                p.author,
                p.genre,
                p.description,
                p.seller_id,
                u.name AS seller_name  -- Join to get seller name
            FROM products p
            LEFT JOIN users u ON p.seller_id = u.user_id
            WHERE p.product_id = %s
        ''', (product_id,))
        product = cursor.fetchone()

        if not product:
            return jsonify({'message': 'Product not found'}), 404

        # Fetch reviews with user details
        cursor.execute("""
            SELECT r.*, 
                u.name,
                u.email,
                u.profile_picture,
                (r.product_quality + r.seller_service + r.delivery_service) / 3 as avg_rating,
                DATE_FORMAT(r.created_at, '%%M %%d, %%Y') as review_date
            FROM reviews r
            JOIN users u ON r.buyer_id = u.user_id
            WHERE r.product_id = %s
            ORDER BY r.created_at DESC
        """, (product_id,))
        reviews = cursor.fetchall()
        product['reviews'] = reviews

        # Check if the product is in user's favorites
        cursor.execute("SELECT 1 FROM favorites WHERE user_id = %s AND product_id = %s", 
                       (user_id, product_id))
        is_favorite = cursor.fetchone() is not None
        product['is_favorite'] = is_favorite

        # Fetch related products
        cursor.execute("""
            SELECT p.*,
                ROUND(COALESCE(AVG((r.product_quality + r.seller_service + r.delivery_service) / 3), 0), 1) as average_rating
            FROM products p
            LEFT JOIN reviews r ON p.product_id = r.product_id
            WHERE p.genre = %s AND p.product_id != %s
            GROUP BY p.product_id
            LIMIT 4
        """, (product['genre'], product_id))
        related_products = cursor.fetchall()
        product['related_products'] = related_products

        return jsonify(product)

    finally:
        cursor.close()
        connection.close()

@app.route('/api/cart/<int:product_id>', methods=['PUT'])
@jwt_required()
def api_update_cart_quantity(product_id):
    user_id = get_jwt_identity()
    data = request.get_json()
    quantity = data.get('quantity')

    if quantity is None or quantity <= 0:
        return jsonify({'error': 'Invalid quantity'}), 400

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
        UPDATE cart
        SET quantity = %s
        WHERE user_id = %s AND product_id = %s
    """, (quantity, user_id, product_id))
    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({'message': 'Cart quantity updated successfully'})

@app.route('/api/cart', methods=['POST'])
@jwt_required()
def api_add_to_cart():
    user_id = get_jwt_identity()
    data = request.get_json()
    product_id = data.get('product_id')
    quantity = data.get('quantity')

    if not product_id or not quantity:
        return jsonify({'error': 'Missing data'}), 400

    connection = get_db_connection()
    cursor = connection.cursor()

    # Check if already in cart
    cursor.execute("SELECT quantity FROM cart WHERE user_id = %s AND product_id = %s", (user_id, product_id))
    existing = cursor.fetchone()

    if existing:
        cursor.execute("""
            UPDATE cart SET quantity = quantity + %s
            WHERE user_id = %s AND product_id = %s
        """, (quantity, user_id, product_id))
    else:
        cursor.execute("""
            INSERT INTO cart (user_id, product_id, quantity)
            VALUES (%s, %s, %s)
        """, (user_id, product_id, quantity))

    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({'message': 'Product added to cart'})


@app.route('/api/checkout', methods=['POST'])
@jwt_required()
def mobile_checkout():
    user_id = get_jwt_identity()
    data = request.get_json()

    cart_items = data.get('cart', [])
    total = data.get('total')

    if not cart_items or not isinstance(cart_items, list):
        return jsonify({'error': 'Invalid cart data'}), 400

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        # Map product_id to quantity
        quantities_map = {str(item['product_id']): int(item['quantity']) for item in cart_items}
        product_ids = list(quantities_map.keys())

        placeholders = ','.join(['%s'] * len(product_ids))
        cursor.execute(f'''
            SELECT p.product_id, p.name, p.price, p.image, p.quantity AS available_quantity
            FROM products p
            WHERE p.product_id IN ({placeholders})
        ''', tuple(product_ids))

        fetched_items = cursor.fetchall()

        # Stock validation
        for item in fetched_items:
            pid = str(item['product_id'])
            if pid not in quantities_map:
                return jsonify({'error': f'Missing quantity for product {pid}'}), 400
            if quantities_map[pid] > item['available_quantity']:
                return jsonify({'error': f'Not enough stock for {item["name"]}'}), 400

        # Get default address
        cursor.execute('''
            SELECT * FROM user_details 
            WHERE user_id = %s AND is_default = TRUE LIMIT 1
        ''', (user_id,))
        address = cursor.fetchone()
        if not address:
            return jsonify({'error': 'No default address found.'}), 400

        shipping_address = f"{address['address']}, {address['barangay']}, {address['city']}, {address['province']}, {address['postcode']}"

        # Insert into orders
        cursor.execute('''
            INSERT INTO orders (buyer_id, total_price, shipping_address, payment_method, status, order_date)
            VALUES (%s, %s, %s, %s, 'pending', NOW())
        ''', (user_id, total, shipping_address, 'cash_on_delivery'))
        order_id = cursor.lastrowid

        # Insert order items and update stock
        for item in fetched_items:
            pid = str(item['product_id'])
            quantity = quantities_map[pid]
            cursor.execute('''
                INSERT INTO order_items (order_id, product_id, quantity, price)
                VALUES (%s, %s, %s, %s)
            ''', (order_id, item['product_id'], quantity, item['price']))
            cursor.execute('''
                UPDATE products SET quantity = quantity - %s WHERE product_id = %s
            ''', (quantity, item['product_id']))

        # Remove purchased items from cart
        cursor.execute(f'''
            DELETE FROM cart 
            WHERE user_id = %s AND product_id IN ({placeholders})
        ''', (user_id,) + tuple(product_ids))

        connection.commit()
        return jsonify({'message': 'Checkout successful', 'order_id': order_id})

    except Exception as e:
        connection.rollback()
        return jsonify({'error': str(e)}), 500

    finally:
        cursor.close()
        connection.close()


@app.route('/api/cart', methods=['GET'])
@jwt_required()
def get_cart():
    user_id = get_jwt_identity()
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # Fetch cart items with product details
    cursor.execute('''
        SELECT 
            c.cart_id,
            p.product_id,
            p.name,
            p.price,
            p.image,
            c.quantity
        FROM cart c
        JOIN products p ON c.product_id = p.product_id
        WHERE c.user_id = %s
    ''', (user_id,))

    cart_items = cursor.fetchall()

    cursor.close()
    connection.close()

    return jsonify(cart_items)


@app.route('/api/favorites', methods=['GET'])
@jwt_required()
@cross_origin()
def api_liked():
    user_id = get_jwt_identity()

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT p.product_id, p.name, p.image, p.price
        FROM favorites f
        JOIN products p ON f.product_id = p.product_id
        WHERE f.user_id = %s
    """, (user_id,))
    
    liked_items = cursor.fetchall()

    return jsonify(liked_items)

@app.route('/api/account', methods=['GET'])
@jwt_required()
@cross_origin()
def get_account():
    user_id = get_jwt_identity()
    print(f"[API] Getting account for user_id: {user_id}")
    
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        # Get basic user info
        cursor.execute("SELECT name, email, gender, date_of_birth, profile_picture FROM users WHERE user_id = %s", (user_id,))
        user_data = cursor.fetchone()
        
        if not user_data:
            print(f"[API] User not found for ID: {user_id}")
            return jsonify({"error": "User not found"}), 404
        
        print(f"[API] Found user data: {user_data}")
        
    
        
        # Get default address
        cursor.execute('''
            SELECT * FROM user_details 
            WHERE user_id = %s AND is_default = TRUE
            LIMIT 1
        ''', (user_id,))
        default_address = cursor.fetchone()
        
        # Add default address to user data
        user_data['default_address'] = default_address
        
        # Add phone from default address if available
        if default_address and 'phone' in default_address:
            user_data['phone'] = default_address['phone']
        else:
            user_data['phone'] = ""
            
        return jsonify(user_data)
        
    except Exception as e:
        print(f"Error fetching account data: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/api/account', methods=['PUT'])
@jwt_required()
@cross_origin()
def update_account():
    user_id = get_jwt_identity()
    data = request.get_json()

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
        UPDATE users
        SET name = %s, gender = %s, phone = %s, birthdate = %s
        WHERE user_id = %s
    """, (data['name'], data['gender'], data['phone'], data['birthdate'], user_id))

    connection.commit()
    return jsonify({'message': 'Profile updated successfully'})


@app.route('/api/promos', methods=['GET'])
def get_promos():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT product_id, name, image
        FROM products
        WHERE is_promo = 1
        LIMIT 5
    """)
    promos = cursor.fetchall()
    return jsonify(promos)


@app.route('/api/products/category/<category>', methods=['GET'])
@cross_origin()
def get_products_by_category(category):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM products WHERE category = %s", (category,))
    products = cursor.fetchall()
    return jsonify(products)

@app.route('/api/orders', methods=['GET'])
@jwt_required()
def get_orders_api():
    user_id = get_jwt_identity()
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute('''
            SELECT o.order_id, o.order_date, o.total_price, o.status,
                   o.shipping_address,
                   oi.quantity, oi.price as item_price, p.name as product_name, p.image, p.product_id
            FROM orders o
            JOIN order_items oi ON o.order_id = oi.order_id
            JOIN products p ON oi.product_id = p.product_id
            WHERE o.buyer_id = %s
            ORDER BY o.order_date DESC
        ''', (user_id,))

        orders_data = cursor.fetchall()

        # Group by order_id
        orders_map = {}
        for row in orders_data:
            order_id = row['order_id']
            if order_id not in orders_map:
                orders_map[order_id] = {
                    'order_id': order_id,
                    'order_date': row['order_date'],
                    'total_price': row['total_price'],
                    'status': row['status'],
                    'shipping_address': row['shipping_address'],
                    'items': []
                }
            orders_map[order_id]['items'].append({
                'product_id': row['product_id'],
                'name': row['product_name'],
                'quantity': row['quantity'],
                'price': row['item_price'],
                'image': row['image']
            })

        return jsonify(list(orders_map.values()))

    except Exception as e:
        print(f"Error fetching orders: {e}")
        return jsonify({'error': 'Failed to fetch orders'}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/api/orders/<int:order_id>', methods=['GET'])
@jwt_required()
def get_order_by_id(order_id):
    user_id = get_jwt_identity()
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        # Fetch the order
        cursor.execute('''
            SELECT o.order_id, o.order_date, o.total_price, o.status,
                   o.shipping_address
            FROM orders o
            WHERE o.order_id = %s AND o.buyer_id = %s
        ''', (order_id, user_id))
        order = cursor.fetchone()
        if not order:
            return jsonify({'error': 'Order not found'}), 404

        # Fetch order items
        cursor.execute('''
            SELECT oi.quantity, oi.price as item_price, p.name as product_name, p.image, p.product_id
            FROM order_items oi
            JOIN products p ON oi.product_id = p.product_id
            WHERE oi.order_id = %s
        ''', (order_id,))
        items = cursor.fetchall()
        order['items'] = [
            {
                'product_id': item['product_id'],
                'name': item['product_name'],
                'quantity': item['quantity'],
                'price': item['item_price'],
                'image': item['image']
            }
            for item in items
        ]

        return jsonify(order)
    except Exception as e:
        print(f"Error fetching order by id: {e}")
        return jsonify({'error': 'Failed to fetch order'}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/api/profile', methods=['GET'])
@jwt_required()
@cross_origin()
def get_profile():
    user_id = get_jwt_identity()
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Get user data including profile picture, gender, and date_of_birth
        cursor.execute("""
            SELECT u.*, ud.phone 
            FROM users u 
            LEFT JOIN user_details ud ON u.user_id = ud.user_id 
            WHERE u.user_id = %s
        """, (user_id,))
        
        user_data = cursor.fetchone()
        
        if user_data:
            # Convert date to string if it exists
            if user_data.get('date_of_birth'):
                user_data['date_of_birth'] = user_data['date_of_birth'].strftime('%Y-%m-%d')
            
            return jsonify({
                'success': True,
                'user': user_data
            })
        
        return jsonify({'success': False, 'error': 'User not found'}), 404
        
    except Exception as e:
        print(f"Error fetching profile: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
        
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route('/api/profile/update', methods=['POST'])
@jwt_required()
@cross_origin()
def update_profile_details():  # Changed from update_profile to update_profile_details
    user_id = get_jwt_identity()
    data = request.get_json()
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Update users table
        users_data = {
            'name': data.get('name'),
            'gender': data.get('gender'),
            'date_of_birth': data.get('date_of_birth')
        }
        users_query = "UPDATE users SET name = %s, gender = %s, date_of_birth = %s WHERE user_id = %s"
        cursor.execute(users_query, (users_data['name'], users_data['gender'], users_data['date_of_birth'], user_id))
        
        # Update or insert into user_details table
        phone = data.get('phone')
        cursor.execute("SELECT 1 FROM user_details WHERE user_id = %s", (user_id,))
        if cursor.fetchone():
            # Update existing record
            cursor.execute("UPDATE user_details SET phone = %s WHERE user_id = %s", (phone, user_id))
        else:
            # Insert new record
            cursor.execute("INSERT INTO user_details (user_id, phone) VALUES (%s, %s)", (user_id, phone))
        
        connection.commit()
        return jsonify({'success': True, 'message': 'Profile updated successfully'})
        
    except Exception as e:
        print(f"Error updating profile: {e}")
        if connection:
            connection.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
        
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()



@app.route('/api/notifications/unread/count', methods=['GET'])
@jwt_required()
@cross_origin()
def get_unread_notification_count():
    user_id = get_jwt_identity()
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        cursor.execute("""
            SELECT COUNT(*) as count 
            FROM notifications 
            WHERE user_id = %s AND is_read = 0
        """, (user_id,))
        
        result = cursor.fetchone()
        count = result[0] if result else 0
        
        return jsonify({'count': count})
        
    except Exception as e:
        print(f"Error getting unread notification count: {e}")
        return jsonify({'error': str(e)}), 500
        
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route('/api/notifications', methods=['GET'])
@jwt_required()
def api_get_notifications():
    user_id = get_jwt_identity()

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute('''
            SELECT 
                notification_id,
                message,
                type,
                order_id,
                created_at,
                is_read
            FROM notifications 
            WHERE user_id = %s 
            ORDER BY created_at DESC
        ''', (user_id,))
        
        notifications = cursor.fetchall()
        return jsonify(notifications)

    except Exception as e:
        print(f"[ERROR] /api/notifications: {e}")
        return jsonify({'error': str(e)}), 500

    finally:
        cursor.close()
        connection.close()

@app.route('/api/notifications/read', methods=['POST'])
@jwt_required()
def api_mark_notification_read():
    user_id = get_jwt_identity()
    data = request.get_json()
    notif_id = data.get('notification_id')

    if not notif_id:
        return jsonify({'error': 'Notification ID is required'}), 400

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute('''
            UPDATE notifications 
            SET is_read = 1 
            WHERE notification_id = %s AND user_id = %s
        ''', (notif_id, user_id))

        connection.commit()
        return jsonify({'success': True})

    except Exception as e:
        print(f"[ERROR] /api/notifications/read: {e}")
        return jsonify({'error': str(e)}), 500

    finally:
        cursor.close()
        connection.close()

@app.route('/api/notifications/delete/<int:notification_id>', methods=['DELETE'])
@jwt_required()
def api_delete_notification(notification_id):
    user_id = get_jwt_identity()

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute('''
            DELETE FROM notifications 
            WHERE notification_id = %s AND user_id = %s
        ''', (notification_id, user_id))

        connection.commit()
        return jsonify({'success': True})

    except Exception as e:
        print(f"[ERROR] /api/notifications/delete: {e}")
        return jsonify({'error': str(e)}), 500

    finally:
        cursor.close()
        connection.close()




@app.route('/api/unread_counts', methods=['GET'])
@jwt_required()
def get_unread_counts_api():
    user_id = get_jwt_identity()
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Notifications
        cursor.execute('''
            SELECT COUNT(*) as count 
            FROM notifications 
            WHERE user_id = %s AND is_read = 0
        ''', (user_id,))
        notif_result = cursor.fetchone()

        # Messages
        cursor.execute('''
            SELECT COUNT(*) as count 
            FROM chat_messages 
            WHERE receiver_id = %s AND status = 'unread'
        ''', (user_id,))
        msg_result = cursor.fetchone()

        return jsonify({
            'notification_count': notif_result['count'] if notif_result else 0,
            'message_count': msg_result['count'] if msg_result else 0
        })

    except Exception as e:
        print(f"[API] Unread count error: {e}")
        return jsonify({'error': str(e)}), 500

    finally:
        if cursor: cursor.close()
        if connection: connection.close()

@app.route('/api/contact_seller/<int:order_id>', methods=['POST'])
@jwt_required()
def api_contact_seller(order_id):
    user_id = get_jwt_identity()
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute('''
            SELECT DISTINCT 
                o.order_id,
                u.user_id as seller_id,
                u.name as seller_name,
                p.name as product_name
            FROM orders o
            JOIN order_items oi ON o.order_id = oi.order_id
            JOIN products p ON oi.product_id = p.product_id
            JOIN users u ON p.seller_id = u.user_id
            WHERE o.order_id = %s AND o.buyer_id = %s
            LIMIT 1
        ''', (order_id, user_id))
        
        seller = cursor.fetchone()
        if not seller:
            return jsonify({'success': False, 'message': 'Seller not found'}), 404

        # Send first inquiry message
        message = f"Inquiry about Order #{order_id} - {seller['product_name']}"
        cursor.execute('''
            INSERT INTO chat_messages (sender_id, receiver_id, message, status, timestamp)
            VALUES (%s, %s, %s, 'unread', NOW())
        ''', (user_id, seller['seller_id'], message))

        connection.commit()
        return jsonify({'success': True, 'seller': {'id': seller['seller_id'], 'name': seller['seller_name']}})

    except Exception as e:
        print(f"[API] Contact seller error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

    finally:
        if cursor: cursor.close()
        if connection: connection.close()

@app.route('/api/messages', methods=['GET'])  
@jwt_required()
@cross_origin()
def api_get_messages():
    user_id = get_jwt_identity()
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute('''
            SELECT 
                cm.*,
                u.name as other_user_name,
                u.profile_picture
            FROM chat_messages cm
            JOIN users u ON 
                CASE 
                    WHEN cm.sender_id = %s THEN cm.receiver_id = u.user_id
                    ELSE cm.sender_id = u.user_id
                END
            WHERE 
                cm.sender_id = %s OR cm.receiver_id = %s
            ORDER BY cm.timestamp DESC
        ''', (user_id, user_id, user_id))
        
        messages = cursor.fetchall()
        
        # Format dates for JSON
        for msg in messages:
            if msg.get('timestamp'):
                msg['timestamp'] = msg['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
        
        return jsonify({
            'success': True,
            'messages': messages
        })
        
    except Exception as e:
        print(f"Error getting messages: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
        
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route('/api/account', methods=['GET'])
@jwt_required()
def get_user_profile():
    user_id = get_jwt_identity()
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute('''
            SELECT 
                u.user_id,
                u.name,
                u.email,
                u.profile_picture,
                u.gender,
                u.date_of_birth,
                ud.phone
            FROM users u
            LEFT JOIN user_details ud ON u.user_id = ud.user_id
            WHERE u.user_id = %s
        ''', (user_id,))
        
        user_data = cursor.fetchone()
        
        if user_data:
            return jsonify(user_data)
        else:
            return jsonify({'error': 'User not found'}), 404
            
    except Exception as e:
        print(f"Error getting user profile: {e}")
        return jsonify({'error': str(e)}), 500
        
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)