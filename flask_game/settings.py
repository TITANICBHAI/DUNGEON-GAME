import os
from dotenv import load_dotenv

load_dotenv()

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL')

# Secret key
SECRET_KEY = os.getenv('SECRET_KEY')

# Other settings for your project
DEBUG = True  # Enable debug mode
ALLOWED_HOSTS = ['*']  # Allow requests from all hosts
