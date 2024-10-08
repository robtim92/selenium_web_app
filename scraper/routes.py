from flask import Blueprint, render_template

scraper_bp = Blueprint('scraper', __name__)

@scraper_bp.route('/scrape')
def scrape():
    return "This is where scraping results will be displayed."
