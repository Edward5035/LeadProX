from flask import Flask, render_template, request, flash, redirect, url_for, session, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import requests
from selectolax.parser import HTMLParser
from urllib.parse import urlparse, urljoin
import re
import time
import json
import random
from bs4 import BeautifulSoup
from collections import Counter
from nltk.util import ngrams
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options



# Flask app setup
app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Dummy user store (now stores any username dynamically)
users = {}

class User(UserMixin):
    def __init__(self, username):
        self.id = username

@login_manager.user_loader
def load_user(user_id):
    return User(user_id) if user_id in users else None












#best----------------------------------------------------------------
# LOGIN


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Simplified login to accept any username/password
        if username and password:
            # Add user to the session
            if username not in users:
                users[username] = generate_password_hash(password)
                
            user = User(username)
            login_user(user)

            # Set default session values to 0 for a fresh session
            session['lead_count'] = 0
            session['email_count'] = 0
            session['phone_count'] = 0
            session['address_count'] = 0
            session['social_media_count'] = 0
            session['company_name_count'] = 0
            
            # Redirect to the index or dashboard after login
            return redirect(url_for('dashboard'))
        
        return 'Invalid credentials', 401
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()  # Logs out the user
    session.clear()  # Clears all session data
    return redirect(url_for('login'))  # Redirects to the login page (or any other page)


#NEW ROUTES-----------–--------------------------------------------

@app.route('/')
def index():
    return render_template('dashboard.html')  # Assuming you have an 'index.html' template


@app.route('/dashboard')
@login_required
def dashboard():
    # Retrieve the qualified_leads_count from the session, defaulting to 0 if not found
    qualified_leads_count = session.get('qualified_leads_count', 0)

    # Render the dashboard template, passing the qualified_leads_count
    return render_template('dashboard.html', 
                           title="Smart Overview", 
                           qualified_leads_count=qualified_leads_count)


@app.route('/leads-generator', endpoint='unique_leads_generator')
@login_required
def leads_generator():
    # Your function logic here
    return render_template('leads_generator.html', title="Leads Generator")



# SALES SECTION------------------


# sales-trends-----------
@app.route('/sales_trends')
def sales_trends():
    return render_template('sales_trends.html')




# sales-analyzer--------------

@app.route('/sales-analyze')
def sales_analyzer():
    return render_template('sales_analyze.html')






# email-accelerator---------------------

@app.route('/email-growth-engine')
def email_growth_engine():
    return render_template('email_growth_engine.html')




# help-support----------------

@app.route('/help-support')
def help_support():
    return render_template('help_support.html')

# NEW FEATURES-------------------------------------------------------------------------------------------------------






#EMAIL SENDER


# Function to send an email
def send_email(smtp_server, port, sender_email, password, receiver_email, subject, body):
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject

    message.attach(MIMEText(body, "plain"))

    with smtplib.SMTP(smtp_server, port) as server:
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())

# Flask route for mass outreach
@app.route('/mass_outreach', methods=['GET', 'POST'])
def mass_outreach():
    if request.method == 'POST':
        sender_email = request.form.get('sender_email')
        password = request.form.get('password')
        subject = request.form.get('subject')
        body = request.form.get('body')
        recipient_emails = request.form.get('recipient_emails').split(',')

        smtp_server = "smtp.gmail.com"
        port = 587

        for receiver_email in recipient_emails:
            send_email(smtp_server, port, sender_email, password, receiver_email.strip(), subject, body)

        return redirect(url_for('mass_outreach_success'))

    return render_template('mass_outreach.html')

@app.route('/mass_outreach_success')
def mass_outreach_success():
    return "Emails sent successfully!"


# Social Scout

import random
import time
import re
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter, Retry
from concurrent.futures import ThreadPoolExecutor, as_completed
from flask import Flask, render_template, request, redirect, url_for
from selenium import webdriver
from selenium.webdriver.chrome.options import Options



# Rotate User Agents to avoid detection
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0"
    # Add more user agents here...
]

# Function to make a request with retries, rotating user agents, and realistic headers
def get_request(url):
    headers = {
        "User-Agent": random.choice(user_agents),
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": url,
        "Connection": "keep-alive",
        "DNT": "1",  # Do Not Track Request Header
    }

    session = requests.Session()
    retry = Retry(connect=5, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    session.headers.update(headers)

    try:
        # Simulate human-like behavior by adding random sleep time
        time.sleep(random.uniform(1, 3))  # Random delay between 1 and 3 seconds
        response = session.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error during request to {url}: {e}")
        return None

# Function to scrape DuckDuckGo search results for social media handles
def scrape_duckduckgo_search(handle):
    search_url = f"https://duckduckgo.com/html?q={handle} site:linkedin.com OR site:twitter.com OR site:instagram.com OR site:facebook.com OR site:tiktok.com OR site:pinterest.com OR site:youtube.com"
    response = get_request(search_url)
    if not response:
        return []
    
    soup = BeautifulSoup(response, 'html.parser')
    leads = []

    for g in soup.find_all('div', class_='result'):
        link_node = g.find('a', class_='result__a')
        description_node = g.find('a', class_='result__snippet')

        if link_node:
            profile_url = link_node['href']
            if any(platform in profile_url for platform in ['linkedin.com', 'twitter.com', 'instagram.com', 'facebook.com', 'tiktok.com', 'pinterest.com', 'youtube.com']):
                leads.append({
                    'social_media_handle': handle,
                    'profile_url': profile_url
                })
    
    return leads

@app.route('/social-scout', methods=['GET', 'POST'])
@login_required
def social_scout():
    if request.method == 'POST':
        handle = request.form.get('social_media_handle')
        if not handle:
            return redirect(url_for('social_scout'))

        # Scrape DuckDuckGo instead of Google for social media profiles
        leads = scrape_duckduckgo_search(handle)

        session = requests.Session()
        retry = Retry(connect=5, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)

        extracted_info = []
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(get_real_info, result['link'], session): result for result in search_results}

            for future in as_completed(futures):
                real_info = future.result()
                if real_info['business_name'] != 'Error':
                    extracted_info.append(real_info)

        # Access robots.txt to mimic common bot behavior using requests
        try:
            robots_url = "https://example.com/robots.txt"
            robots_response = get_request(robots_url)
            if robots_response:
                print("Accessed robots.txt successfully.")
        except requests.exceptions.RequestException as e:
            print(f"Error accessing robots.txt: {e}")

        # Simulate scrolling using headless Selenium
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run headlessly
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument(f"user-agent={random.choice(user_agents)}")

        driver = webdriver.Chrome(options=chrome_options)
        driver.get("https://example.com")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(random.uniform(1, 3))  # Random delay
        driver.quit()

        return render_template('social_scout.html', title="Social Media Search", leads=leads)

    return render_template('social_scout.html', title="Social Media Search")




# AI LEADFINDER
import time
from flask import Flask, render_template, request, session
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options


# Scraping function to get business data
def scrape_data(industry, location):
    options = Options()
    options.add_argument('--headless')  # Run headless without opening a browser window
    options.add_argument('--disable-gpu')

    # Set up WebDriver using WebDriverManager
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    # Open Yellow Pages website
    url = 'https://www.yellowpages.com/'
    driver.get(url)
    time.sleep(3)

    # Find the search bar and input the industry (business type)
    search_box = driver.find_element(By.NAME, "search_terms")
    search_box.send_keys(industry)

    # Find the location input field and enter the location
    location_box = driver.find_element(By.NAME, "geo_location_terms")
    location_box.clear()
    location_box.send_keys(location)

    # Press Enter to initiate the search
    search_box.send_keys(Keys.RETURN)
    time.sleep(3)

    # Extract the list of results
    business_list = driver.find_elements(By.CSS_SELECTOR, '.info')

    # List to hold the scraped business data
    scraped_data = []

    # Loop through each business and extract data
    for business in business_list:
        name = business.find_element(By.CSS_SELECTOR, '.business-name').text
        phone = business.find_element(By.CSS_SELECTOR, '.phone').text if business.find_elements(By.CSS_SELECTOR, '.phone') else "N/A"
        address = business.find_element(By.CSS_SELECTOR, '.street-address').text if business.find_elements(By.CSS_SELECTOR, '.street-address') else "N/A"
        website = business.find_element(By.CSS_SELECTOR, '.links a').get_attribute('href') if business.find_elements(By.CSS_SELECTOR, '.links a') else "N/A"
        
        # Social media links (Facebook, Twitter, Instagram, etc.)
        social_links = {}
        social_elements = business.find_elements(By.CSS_SELECTOR, '.social-icons a')
        
        for social in social_elements:
            url = social.get_attribute('href')
            if "facebook" in url:
                social_links['facebook'] = url
            elif "twitter" in url:
                social_links['twitter'] = url
            elif "instagram" in url:
                social_links['instagram'] = url
            elif "linkedin" in url:
                social_links['linkedin'] = url
            # You can add more conditions for other social media platforms if needed

        # Append the extracted data to the list
        scraped_data.append({
            "name": name,
            "phone": phone,
            "address": address,
            "website": website,
            "social_links": social_links
        })

    # Close the driver
    driver.quit()
    
    return scraped_data

@app.route('/leadfinder', methods=['GET', 'POST'])
def leadfinder():
    industry = ''
    location = ''
    business_data = []

    if request.method == 'POST':
        # Get the input data from the form
        industry = request.form['industry']
        location = request.form['location']
        
        # Ensure that the industry and location are not empty before scraping
        if industry and location:
            business_data = scrape_data(industry, location)

            # Store the count of business names in session
            session['business_name_count'] = len(business_data)
        else:
            business_data = []  # No data to scrape if either is empty

    # Render the template with the scraped data
    return render_template('leadfinder.html', business_data=business_data, industry=industry, location=location)

@app.route('/insights')
def insights():
    return render_template('dashboard.html', 
                           business_name_count=session.get('business_name_count', 0))



# Lead Qualifier
from flask import Flask, render_template, request, session
import re
import random



# Function to qualify leads and assign conversion rates
def qualify_lead_data(lead_info):
    score = 0
    qualification_status = ''

    if 'emails' in lead_info and lead_info['emails']:
        score += len(lead_info['emails']) * random.randint(10, 20)
    if 'phone_numbers' in lead_info and lead_info['phone_numbers']:
        score += len(lead_info['phone_numbers']) * random.randint(5, 15)
    if 'address' in lead_info and lead_info['address']:
        score += random.randint(20, 30)
    if 'social_media' in lead_info and lead_info['social_media']:
        score += len(lead_info['social_media']) * random.randint(10, 20)
    
    # Add a random bonus to some leads
    score += random.randint(0, 15)
    
    if score >= 50:
        qualification_status = 'High'
    elif 30 <= score < 50:
        qualification_status = 'Medium'
    else:
        qualification_status = 'Low'

    return {
        'score': score,
        'qualification_status': qualification_status,
        'conversion_rate': 100 if qualification_status == 'High' else (60 if qualification_status == 'Medium' else 30),
        'ai_feedback': f"The lead has a {qualification_status} qualification potential."
    }

# Function to parse leads from the raw text input
def parse_lead_data(leads_text):
    leads = []
    lead_entries = re.split(r'Website:\s?.*\n', leads_text)

    for entry in lead_entries:
        if entry.strip():
            lead_info = {
                'company_name': None,
                'emails': [],
                'phone_numbers': [],
                'address': [],
                'social_media': []
            }

            lines = entry.strip().split('\n')
            
            if lines:
                lead_info['company_name'] = lines[0].strip()

                for line in lines:
                    if line.startswith("Phone:"):
                        phone_matches = re.findall(r'\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{4}', line)
                        lead_info['phone_numbers'].extend(phone_matches)
                    if line.startswith("Address:"):
                        address_match = re.findall(r'Address:\s(.+)', line)
                        if address_match:
                            lead_info['address'].append(address_match[0])
                    if line.startswith("Website:"):
                        social_media_matches = re.findall(r'Website:\s(.+)', line)
                        if social_media_matches:
                            lead_info['social_media'].append(social_media_matches[0])

            leads.append(lead_info)

    return leads

@app.route('/qualify_new_leads', methods=['GET', 'POST'])
def qualify_new_leads():
    results = []

    if request.method == 'POST':
        leads_text = request.form.get('leads', '')
        file = request.files.get('file')

        if file:
            leads_text = file.read().decode('utf-8')

        if leads_text.strip():
            lead_infos = parse_lead_data(leads_text)

            for lead_info in lead_infos:
                qualification_info = qualify_lead_data(lead_info)
                results.append({
                    'company_name': lead_info.get('company_name', 'No Company Name'),
                    'score': qualification_info['score'],
                    'qualification_status': qualification_info['qualification_status'],
                    'conversion_rate': qualification_info['conversion_rate'],
                    'email': ', '.join(lead_info.get('emails', [])) or 'N/A',
                    'phone': ', '.join(lead_info.get('phone_numbers', [])) or 'N/A',
                    'address': ', '.join(lead_info.get('address', [])) or 'N/A',
                    'social_media': ', '.join(lead_info.get('social_media', [])) or 'N/A',
                    'ai_feedback': qualification_info['ai_feedback']
                })

    return render_template('leadqualifier.html', results=results)


# VALIDATE LEADS-----------------
from flask import Flask, render_template, request
import re
import random



# Function to validate leads
def validate_lead_data(lead_info):
    valid = True
    validation_errors = []

    # Email Validation
    if not lead_info.get('emails'):
        valid = False
        validation_errors.append('Missing email')

    # Phone Number Validation
    if not lead_info.get('phone_numbers'):
        valid = False
        validation_errors.append('Missing phone number')

    # Address Validation
    if not lead_info.get('address'):
        valid = False
        validation_errors.append('Missing address')

    # Social Media Validation
    if not lead_info.get('social_media'):
        valid = False
        validation_errors.append('Missing social media link')

    return valid, validation_errors

# Function to parse leads from the raw text input
def parse_lead_data(leads_text):
    leads = []
    lead_entries = re.split(r'Website:\s?.*\n', leads_text)

    for entry in lead_entries:
        if entry.strip():
            lead_info = {
                'company_name': None,
                'emails': [],
                'phone_numbers': [],
                'address': [],
                'social_media': []
            }

            lines = entry.strip().split('\n')
            
            if lines:
                lead_info['company_name'] = lines[0].strip()

                for line in lines:
                    if line.startswith("Phone:"):
                        phone_matches = re.findall(r'\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{4}', line)
                        lead_info['phone_numbers'].extend(phone_matches)
                    if line.startswith("Address:"):
                        address_match = re.findall(r'Address:\s(.+)', line)
                        if address_match:
                            lead_info['address'].append(address_match[0])
                    if line.startswith("Website:"):
                        social_media_matches = re.findall(r'Website:\s(.+)', line)
                        if social_media_matches:
                            lead_info['social_media'].append(social_media_matches[0])

            leads.append(lead_info)

    return leads

@app.route('/validate_leads', methods=['GET', 'POST'])
def validate_leads():
    validation_results = []

    if request.method == 'POST':
        leads_text = request.form.get('leads', '')
        file = request.files.get('file')

        if file:
            leads_text = file.read().decode('utf-8')

        if leads_text.strip():
            lead_infos = parse_lead_data(leads_text)

            for lead_info in lead_infos:
                valid, validation_errors = validate_lead_data(lead_info)
                validation_results.append({
                    'company_name': lead_info.get('company_name', 'No Company Name'),
                    'valid': valid,
                    'validation_errors': validation_errors,
                    'email': ', '.join(lead_info.get('emails', [])) or 'N/A',
                    'phone': ', '.join(lead_info.get('phone_numbers', [])) or 'N/A',
                    'address': ', '.join(lead_info.get('address', [])) or 'N/A',
                    'social_media': ', '.join(lead_info.get('social_media', [])) or 'N/A',
                })

    return render_template('validate_leads.html', validation_results=validation_results)




#COMPETITOR ANALYSIS----------------------
import re
import time
from flask import Flask, render_template, request
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import requests
import random

# List of user agents for rotation
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0"
]

# List of keywords to exclude directory-style and large global websites
exclude_keywords = [
    "directory", "listing", "top", "best", "guide", "reviews", "wiki", "global", "international",
    "yelp", "tripadvisor", "yellowpages", "linkedin", "facebook", "twitter"
]

# Function to perform a request with retries and rotating user agents
def perform_request(url):
    headers = {
        "User-Agent": random.choice(user_agents),
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
        "DNT": "1",  # Do Not Track Request Header
    }

    session = requests.Session()
    retry_strategy = requests.adapters.Retry(total=3, backoff_factor=1)
    adapter = requests.adapters.HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    try:
        response = session.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error during request to {url}: {e}")
        return None

# Function to extract meta description
def extract_meta_description(url):
    description = "N/A"
    page_content = perform_request(url)
    if page_content:
        soup = BeautifulSoup(page_content, 'html.parser')
        meta_tag = soup.find('meta', attrs={'name': 'description'})
        if meta_tag and 'content' in meta_tag.attrs:
            description = meta_tag['content']
        else:
            description = "Description not available"
    return description

# Function to calculate score for each competitor
def calculate_score(business, location):
    score = 0

    # Service Completeness
    if business['services'] != "N/A":
        if len(business['services'].split(',')) > 3:
            score += 5
        else:
            score += 3

    # Website Quality
    if any(keyword in business['website'].lower() for keyword in exclude_keywords):
        score += 2
    else:
        score += 1

    # User Engagement
    if any(phrase in business['services'].lower() for phrase in ["contact", "call", "book", "get a quote", "visit", "find out more"]):
        score += 2

    # Local Relevance
    if location.lower() in business['services'].lower() or location.lower() in business['name'].lower():
        score += 3

    return score

# Scraping function to get business data from Bing and rank competitors
def scrape_business_data_bing(industry, location):
    options = Options()
    options.add_argument('--headless')  # Run headless without opening a browser window
    options.add_argument('--disable-gpu')

    # Set up WebDriver using WebDriverManager
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    # Open Bing and perform a search
    query = f"{industry} in {location}"
    url = f"https://www.bing.com/search?q={query}"
    driver.get(url)
    time.sleep(3)

    # Extract the list of results
    business_list = driver.find_elements(By.CSS_SELECTOR, '.b_algo')

    # List to hold the scraped business data
    scraped_data = []

    # Loop through each business and extract data
    for business in business_list:
        name = business.find_element(By.CSS_SELECTOR, 'h2').text
        website = business.find_element(By.CSS_SELECTOR, 'h2 a').get_attribute('href') if business.find_elements(By.CSS_SELECTOR, 'h2 a') else "N/A"
        
        # Filter out directory-style and large global websites
        if any(keyword in website.lower() for keyword in exclude_keywords):
            continue

        # Extract meta description as services
        services = extract_meta_description(website) if website != "N/A" else "N/A"

        # Append the extracted data to the list
        scraped_data.append({
            "name": name,
            "website": website,
            "services": services,
        })

    # Close the driver
    driver.quit()

    # Calculate scores and sort the businesses by score
    for business in scraped_data:
        business['score'] = calculate_score(business, location)

    scraped_data.sort(key=lambda x: x['score'], reverse=True)
    
    return scraped_data



@app.route('/businessfinder', methods=['GET', 'POST'])
def business_finder():
    industry = ''
    location = ''
    business_data = []

    if request.method == 'POST':
        # Get the input data from the form
        industry = request.form['industry']
        location = request.form['location']
        
        # Ensure that the industry and location are not empty before scraping
        if industry and location:
            business_data = scrape_business_data_bing(industry, location)
        else:
            business_data = []  # No data to scrape if either is empty

    # Render the template with the scraped data
    return render_template('businessfinder.html', business_data=business_data, industry=industry, location=location)

@app.route('/competitor_analysis', methods=['GET', 'POST'])
def competitor_analysis():
    industry = ''
    location = ''
    business_data = []

    if request.method == 'POST':
        # Get the input data from the form
        industry = request.form['industry']
        location = request.form['location']
        
        # Ensure that the industry and location are not empty before scraping
        if industry and location:
            business_data = scrape_business_data_bing(industry, location)
        else:
            business_data = []  # No data to scrape if either is empty

    # Render the template with the scraped data
    return render_template('competitoranalysis.html', business_data=business_data, industry=industry, location=location)


# SEO BOOST---------------------------

import re
import time
from flask import Flask, render_template, request
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import requests
import random
from collections import Counter



# Define stopwords directly
stop_words = set([
    'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours', 'yourself', 'yourselves',
    'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 'itself', 'they', 'them', 'their',
    'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are', 'was',
    'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the',
    'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against',
    'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in',
    'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why',
    'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only',
    'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', 'should', 'now'
])

# List of user agents for rotation
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0"
]

# Function to perform a request with retries and rotating user agents
def perform_http_request(url):
    headers = {
        "User-Agent": random.choice(user_agents),
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
        "DNT": "1",  # Do Not Track Request Header
    }

    session = requests.Session()
    retry_strategy = requests.adapters.Retry(total=3, backoff_factor=1)
    adapter = requests.adapters.HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    try:
        response = session.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error during request to {url}: {e}")
        return None

# Function to extract keywords from the homepage
def fetch_keywords(url):
    page_content = perform_http_request(url)
    if not page_content:
        return []

    soup = BeautifulSoup(page_content, 'html.parser')
    text = soup.get_text()
    
    # Tokenize text and remove stopwords
    words = re.findall(r'\b\w+\b', text.lower())
    keywords = [word for word in words if word.isalnum() and word not in stop_words]
    
    # Get keyword frequency
    keyword_freq = Counter(keywords)
    ranked_keywords = keyword_freq.most_common()
    
    return ranked_keywords

# Scraping function to get business data from Bing and rank keywords
def gather_business_data(industry, location):
    options = Options()
    options.add_argument('--headless')  # Run headless without opening a browser window
    options.add_argument('--disable-gpu')

    # Set up WebDriver using WebDriverManager
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    # Open Bing and perform a search
    query = f"{industry} in {location}"
    url = f"https://www.bing.com/search?q={query}"
    driver.get(url)
    time.sleep(3)

    # Extract the list of results
    business_list = driver.find_elements(By.CSS_SELECTOR, '.b_algo')

    # List to hold the scraped business data
    scraped_data = []

    # Loop through each business and extract data
    for business in business_list:
        name = business.find_element(By.CSS_SELECTOR, 'h2').text
        website = business.find_element(By.CSS_SELECTOR, 'h2 a').get_attribute('href') if business.find_elements(By.CSS_SELECTOR, 'h2 a') else "N/A"
        
        # Skip if no valid website
        if website == "N/A":
            continue

        # Extract and rank keywords from the homepage
        keywords = fetch_keywords(website)

        # Calculate keyword percentages
        total_keywords = sum([freq for _, freq in keywords])
        keyword_percentages = [(keyword, freq / total_keywords * 100) for keyword, freq in keywords]

        # Append the extracted data to the list
        scraped_data.append({
            "name": name,
            "website": website,
            "keywords": keyword_percentages
        })

    # Close the driver
    driver.quit()
    
    return scraped_data

@app.route('/seorocket', methods=['GET', 'POST'])
def seorocket():
    industry = ''
    location = ''
    business_data = []

    if request.method == 'POST':
        # Get the input data from the form
        industry = request.form['industry']
        location = request.form['location']
        
        # Ensure that the industry and location are not empty before scraping
        if industry and location:
            business_data = gather_business_data(industry, location)
        else:
            business_data = []  # No data to scrape if either is empty

    # Split keywords into short-tail and long-tail keywords
    short_tail = []
    long_tail = []
    keyword_percentages = {}

    if business_data:
        for business in business_data:
            for keyword, percentage in business['keywords']:
                keyword_percentages[keyword] = percentage
                if len(keyword.split()) <= 2:  # Short-tail if 1-2 words
                    short_tail.append(keyword)
                else:
                    long_tail.append(keyword)
                    print(f"Identified long-tail keyword: {keyword}")  # Debugging print

    # Render the template with the scraped data
    return render_template('seorocket.html', business_data=business_data, industry=industry, location=location, keyword_percentages=keyword_percentages, short_tail=short_tail, long_tail=long_tail)



# CONTACT FINDER--------------------------------------
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse
from flask import Flask, render_template, request, redirect, url_for, session
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC



# Function to initialize Selenium WebDriver with headless options
def init_webdriver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(options=chrome_options)

# Function to scrape Bing search results using Selenium WebDriver
def scrape_bing_search(query):
    driver = init_webdriver()
    search_url = f"https://www.bing.com/search?q={query}"
    
    try:
        driver.get(search_url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'b_algo')))
        soup = BeautifulSoup(driver.page_source, 'html.parser')
    finally:
        driver.quit()

    results = []

    for result in soup.find_all('li', class_='b_algo'):
        title = result.find('h2').get_text() if result.find('h2') else 'No title'
        link = result.find('a')['href'] if result.find('a') else 'No link'
        domain = urlparse(link).netloc
        description = result.find('p').get_text() if result.find('p') else 'No description'

        if "best" not in title.lower() and "directory" not in title.lower() and "list" not in title.lower():
            if "yelp.com" not in domain and "tripadvisor.com" not in domain:
                results.append({
                    'title': title,
                    'link': link,
                    'domain': domain,
                    'description': description
                })

    return results

# Function to check if a URL is valid
def is_valid_url(url):
    parsed_url = urlparse(url)
    return parsed_url.scheme in ("http", "https")

# Function to extract contact information
def extract_contact_info(url):
    if not is_valid_url(url):
        return {"error": "Invalid URL"}

    driver = init_webdriver()
    
    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        soup = BeautifulSoup(driver.page_source, 'html.parser')
    except selenium.common.exceptions.WebDriverException as e:
        if "unsupported protocol" in str(e):
            return {"error": "Unsupported protocol in URL"}
        else:
            raise
    finally:
        driver.quit()

    # Extract emails
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(email_pattern, soup.get_text())

    # Extract phone numbers
    phone_pattern = r'\+?[0-9.\-\(\) ]{7,}'
    phone_numbers = re.findall(phone_pattern, soup.get_text())
    
    # Extract social media links using BeautifulSoup and additional patterns
    social_media_domains = ["twitter.com", "facebook.com", "linkedin.com", "instagram.com"]
    social_media_links = []

    for link in soup.find_all('a', href=True):
        href = link['href']
        if any(domain in href for domain in social_media_domains):
            social_media_links.append(href)

    # Check meta tags for social media links
    meta_tags = soup.find_all('meta', attrs={'property': 'og:url'})
    for tag in meta_tags:
        content = tag.get('content', '')
        if any(domain in content for domain in social_media_domains):
            social_media_links.append(content)

    # Extract addresses (simple regex for demonstration)
    address_pattern = r'\d{1,5}\s\w+\s\w+'
    addresses = re.findall(address_pattern, soup.get_text())
    
    # Extract company name
    company_name = soup.title.string if soup.title else "N/A"
    
    return {
        "emails": emails, 
        "phone_numbers": phone_numbers, 
        "addresses": addresses,
        "social_media_links": social_media_links,
        "company_name": company_name, 
        "domain": url
    }

# Flask route for contact information
@app.route('/contactfinder', methods=['GET', 'POST'])
def contact_finder():
    if request.method == 'POST':
        industry = request.form.get('industry')
        location = request.form.get('location')
        if not industry or not location:
            return redirect(url_for('contact_finder'))

        query = f"{industry} {location}"
        search_results = scrape_bing_search(query)

        extracted_info = []
        for result in search_results:
            contact_info = extract_contact_info(result['link'])
            if contact_info.get('company_name') and contact_info['company_name'] != "N/A":
                extracted_info.append(contact_info)

        # Store leads data in session
        session['leads'] = extracted_info
        session['lead_count'] = len(extracted_info)
        session['email_count'] = sum(len(info.get('emails', [])) for info in extracted_info)
        session['phone_count'] = sum(len(info.get('phone_numbers', [])) for info in extracted_info)
        session['address_count'] = sum(len(info.get('addresses', [])) for info in extracted_info)
        session['social_media_count'] = sum(len(info.get('social_media_links', [])) for info in extracted_info)
        session['company_name_count'] = sum(1 for info in extracted_info if info.get('company_name'))

        return render_template('contactfinder.html', title="Contact Finder", business_data=extracted_info)

    return render_template('contactfinder.html', title="Contact Finder", business_data=[])

# Flask route for dashboard
@app.route('/dashboard2')
def dashboard2():
    return render_template('dashboard.html', 
                           lead_count=session.get('lead_count', 0),
                           email_count=session.get('email_count', 0),
                           phone_count=session.get('phone_count', 0),
                           address_count=session.get('address_count', 0),
                           social_media_count=session.get('social_media_count', 0),
                           company_name_count=session.get('company_name_count', 0))







# SOCIAL INSIGHTS----------------------------------------------
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse
from flask import Flask, render_template, request, redirect, url_for
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC



def initialize_webdriver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(options=chrome_options)

def bing_search(query):
    driver = initialize_webdriver()
    search_url = f"https://www.bing.com/search?q={query}"
    
    try:
        driver.get(search_url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'b_algo')))
        soup = BeautifulSoup(driver.page_source, 'html.parser')
    finally:
        driver.quit()

    results = []

    for result in soup.find_all('li', class_='b_algo'):
        title = result.find('h2').get_text() if result.find('h2') else 'No title'
        link = result.find('a')['href'] if result.find('a') else 'No link'
        domain = urlparse(link).netloc

        if "best" not in title.lower() and "directory" not in title.lower() and "list" not in title.lower():
            if "yelp.com" not in domain and "tripadvisor.com" not in domain:
                results.append({
                    'title': title,
                    'link': link,
                    'domain': domain
                })

    return results

def get_contact_info(url):
    driver = initialize_webdriver()
    
    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        soup = BeautifulSoup(driver.page_source, 'html.parser')
    finally:
        driver.quit()

    # Extract company name
    company_name = soup.title.string if soup.title else "N/A"

    # Extract social media links
    social_media_links = []
    for a in soup.find_all('a', href=True):
        href = a['href']
        if any(social in href for social in ['facebook.com', 'twitter.com', 'linkedin.com', 'instagram.com']):
            social_media_links.append(href)
    
    return {"company_name": company_name, "domain": url, "social_media_links": social_media_links}

@app.route('/socialinsights', methods=['GET', 'POST'])
def social_insights():
    if request.method == 'POST':
        industry = request.form.get('industry')
        location = request.form.get('location')
        if not industry or not location:
            return redirect(url_for('social_insights'))

        query = f"{industry} {location}"
        search_results = bing_search(query)

        extracted_info = []
        for result in search_results:
            contact_info = get_contact_info(result['link'])
            if contact_info['company_name'] != "N/A":
                extracted_info.append(contact_info)

        return render_template('socialinsights.html', title="Social Insights", business_data=extracted_info)

    return render_template('socialinsights.html', title="Social Insights", business_data=[])








if __name__ == '__main__':
    app.run(threaded=True)
