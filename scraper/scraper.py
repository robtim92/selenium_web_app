# scraper/scraper.py

import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import multiprocessing

def get_coordinates_from_city(city_name):
    """
    Fetches latitude and longitude for a given city name using OpenStreetMap's API.
    """
    base_url = "https://nominatim.openstreetmap.org/search"
    params = {
        'q': city_name,
        'format': 'json',
        'limit': 1
    }
    headers = {
        'User-Agent': 'localsearch/1.0 (your-email@gmail.com)',
    }
    response = requests.get(base_url, params=params, headers=headers)
    if response.status_code == 200 and response.json():
        data = response.json()[0]
        return float(data['lat']), float(data['lon'])
    else:
        return None, None

def set_geolocation(driver, latitude, longitude, accuracy=100):
    """
    Sets the geolocation in the Selenium WebDriver instance.
    """
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "accuracy": accuracy
    }
    driver.execute_cdp_cmd("Emulation.setGeolocationOverride", params)

def get_google_search_results_selenium(keyword, latitude=None, longitude=None, driver=None):
    """
    Uses Selenium to perform a Google search and return results.
    If latitude and longitude are provided, sets geolocation.
    """
    close_driver = False
    if not driver:
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-software-rasterizer')
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        close_driver = True

    try:
        if latitude is not None and longitude is not None:
            set_geolocation(driver, latitude, longitude)

        driver.get("https://www.google.com")

        # Wait for the search box to be present before interacting
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "q"))
        )
        search_box.clear()
        search_box.send_keys(keyword + Keys.RETURN)

        # Wait for the results to appear
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'span.CSkcDe'))
        )

        # Extract results
        autofill_suggestions = [element.text for element in driver.find_elements(By.CSS_SELECTOR, 'div.wM6W7d span')]
        paa_questions = [element.text for element in driver.find_elements(By.CSS_SELECTOR, 'span.CSkcDe')]
        related_searches = [element.text for element in driver.find_elements(By.CSS_SELECTOR, 'div.s75CSd.u60jwe.r2fjmd.AB4Wff')]

        # Add message if no PAA results are found
        if not paa_questions:
            paa_questions = ["No 'People Also Ask' results found for this query."]

    except (NoSuchElementException, TimeoutException) as e:
        print(f"Error during scraping: {e}")
        return {'query': keyword, 'autofill_suggestions': [], 'paa_questions': ["An error occurred during scraping."], 'related_searches': [], 'error': str(e)}
    finally:
        if close_driver and driver:
            try:
                driver.quit()
            except Exception as e:
                print(f"Error closing driver: {e}")

    return {'query': keyword, 'autofill_suggestions': autofill_suggestions, 'paa_questions': paa_questions, 'related_searches': related_searches}

def fetch_recursive_search_data(term, depth, max_depth, driver, latitude=None, longitude=None):
    """
    Helper function for recursive search with threading.
    """
    return recursive_search(term, depth + 1, max_depth, driver, latitude=latitude, longitude=longitude)

def recursive_search(keyword, depth=1, max_depth=3, driver=None, latitude=None, longitude=None):
    """
    Recursively fetches search results using PAA questions and related searches.
    """
    results = [get_google_search_results_selenium(keyword, latitude, longitude, driver)]
    if depth < max_depth:
        terms = results[0]['paa_questions'] + results[0]['related_searches']
        max_workers = min(5, multiprocessing.cpu_count() * 2)

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_term = {
                executor.submit(fetch_recursive_search_data, term, depth, max_depth, driver, latitude, longitude): term
                for term in terms
            }
            for future in as_completed(future_to_term):
                results.extend(future.result())

    return results
