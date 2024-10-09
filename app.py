# app.py

import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from scraper.scraper import recursive_search, get_coordinates_from_city

load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

env = os.getenv('FLASK_ENV', 'development')

if env == 'production':
    app.config.from_object('config.ProductionConfig')
else:
    app.config.from_object('config.DevelopmentConfig')

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

@app.route('/')
def home():
    """Renders the home page template."""
    return render_template('home.html')

@app.route('/scrape', methods=['POST'])
def scrape():
    """Handles user input and triggers the scraping process."""
    content_type = request.headers.get('Content-Type', '')
    if 'application/json' not in content_type:
        app.logger.error("Invalid content type: %s", content_type)
        return jsonify({"error": "Content-Type must be 'application/json'"}), 415

    data = request.get_json()
    if not data:
        app.logger.error("Invalid JSON data received.")
        return jsonify({"error": "Invalid JSON format"}), 400

    keyword = data.get('keyword', '')
    city_name = data.get('city_name', '')
    latitude, longitude = get_coordinates_from_city(city_name) if city_name else (None, None)

    driver = None
    results = recursive_search(keyword, max_depth=2, driver=driver, latitude=latitude, longitude=longitude)

    if results:
        app.logger.info("Scraping completed successfully for keyword: %s", keyword)
        return jsonify(results=results), 200
    else:
        app.logger.error("Scraping failed for keyword: %s", keyword)
        return jsonify(message="An error occurred during scraping."), 500

if __name__ == '__main__':
    app.run()
