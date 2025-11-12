import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///colprad.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Mail settings
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True') == 'True'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    
    # PayGate settings
    PAYGATE_API_KEY = os.environ.get('PAYGATE_API_KEY')
    PAYGATE_MERCHANT_ID = os.environ.get('PAYGATE_MERCHANT_ID')
    PAYGATE_WEBHOOK_SECRET = os.environ.get('PAYGATE_WEBHOOK_SECRET')
    
    # App settings
    TICKETS_PER_PAGE = 20
    SUPPORTED_LANGUAGES = ['fr', 'en']
    DEFAULT_LANGUAGE = 'fr'
    
    # Ticket types and prices (FCFA)
    TICKET_TYPES = {
        'standard': {'name': 'Standard', 'price': 5000, 'quota': 200, 'color': '#FFFFFF'},
        'premium': {'name': 'Premium', 'price': 15000, 'quota': 100, 'color': '#9E9E9E'},
        'vip': {'name': 'VIP', 'price': 50000, 'quota': 50, 'color': '#D4AF37'}
    }
    
    # Badge colors
    BADGE_COLORS = {
        'vip': '#D4AF37',
        'premium': '#9E9E9E',
        'standard': '#FFFFFF',
        'staff': '#0057A6',
        'hotesse': '#FF7F11',
        'presse': '#8B0000'
    }
