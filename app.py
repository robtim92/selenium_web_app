# app.py

import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from dotenv import load_dotenv
from config import DevelopmentConfig, ProductionConfig

load_dotenv()  # Load variables from .env file

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# Determine the environment (development or production)
env = os.getenv('FLASK_ENV', 'development')

if env == 'production':
    app.config.from_object(ProductionConfig)
else:
    app.config.from_object(DevelopmentConfig)

# Logging setup
if not os.path.exists('logs'):
    os.mkdir('logs')

file_handler = RotatingFileHandler(
    'logs/flask_app.log', maxBytes=10240, backupCount=10
)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)

app.logger.setLevel(logging.INFO)
app.logger.info('Flask application startup')

# Placeholder for other imports, routes, or logic

if __name__ == '__main__':
    app.run()
