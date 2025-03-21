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
from datetime import timedelta


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

            # Clear session variables related to data
            session.pop('results', None)
            session.pop('query', None)
            session.pop('email_count', None)
            session.pop('phone_count', None)
            session.pop('address_count', None)
            
            # Redirect to the index or dashboard after login
            return redirect(url_for('dashboard'))
        
        return 'Invalid credentials', 401
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()  # Logs out the user
  
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




#PEOPLE SEARCH--------------------------------------------------------------------------------------------------------
import random
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from flask import Flask, render_template, request, redirect, url_for, session
from fake_useragent import UserAgent
import re

# Create a user-agent manager instance for dynamic user-agent rotation
user_agents = UserAgent()

# Function to generate random headers and simulate human-like browsing
def generate_random_headers():
    user_agents_list = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/89.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0",
        "Mozilla/5.0 (Linux; Android 10; Pixel 3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.127 Mobile Safari/537.36",
        # Add more user agents as needed
    ]
    headers = {
        "User-Agent": random.choice(user_agents_list),  # Choose randomly from the list
        "Accept-Language": random.choice(["en-US", "en-GB", "en-CA"]),
        "Connection": "keep-alive",
        "DNT": "1",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Referer": "https://www.google.com",
        "Upgrade-Insecure-Requests": "1",
    }
    return headers

# Function to perform the HTTP request with retry logic, randomized delays, and headers
def make_http_request(url):
    headers = generate_random_headers()

    session = requests.Session()
    retry_strategy = requests.adapters.Retry(total=5, backoff_factor=2)  # Increased retries and backoff
    adapter = requests.adapters.HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    time.sleep(random.uniform(2, 5))  # Add randomized delay to simulate human browsing

    try:
        response = session.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error during request to {url}: {e}")
        return None

# Function to scrape search results using requests and BeautifulSoup
def get_search_results(query):
    search_url = f"https://www.bing.com/search?q={query}"
    page_content = make_http_request(search_url)

    if not page_content:
        return []

    soup = BeautifulSoup(page_content, 'html.parser')
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

# Function to validate URLs
def validate_url(url):
    parsed_url = urlparse(url)
    return parsed_url.scheme in ("http", "https")

# Function to extract contact information from a URL
def extract_contact_info(url):
    if not validate_url(url):
        return {"error": "Invalid URL"}

    page_content = make_http_request(url)
    if not page_content:
        return {"error": "Unable to fetch page"}

    soup = BeautifulSoup(page_content, 'html.parser')
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    phone_pattern = r'\+?[0-9.\-\(\) ]{7,}'
    social_media_domains = ["twitter.com", "facebook.com", "linkedin.com", "instagram.com"]

    emails = re.findall(email_pattern, soup.get_text())
    phone_numbers = re.findall(phone_pattern, soup.get_text())

    social_media_links = []
    for link in soup.find_all('a', href=True):
        href = link['href']
        if any(domain in href for domain in social_media_domains):
            social_media_links.append(href)

    address_pattern = r'\d{1,5}\s\w+\s\w+'
    addresses = re.findall(address_pattern, soup.get_text())
    company_name = soup.title.string if soup.title else "N/A"

    return {
        "emails": emails,
        "phone_numbers": phone_numbers,
        "addresses": addresses,
        "social_media_links": social_media_links,
        "company_name": company_name,
        "domain": url
    }

# Flask route for lead generation page
@app.route('/people_search', methods=['GET', 'POST'])
@login_required
def people_search():
    if request.method == 'POST':
        industry = request.form.get('industry')
        location = request.form.get('location')
        
        if not industry or not location:
            return redirect(url_for('lead_form'))  # Redirect if fields are missing

        query = f"{industry} {location}"
        search_results = get_search_results(query)

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

        return render_template('people_search.html', title="Lead Generator", business_data=extracted_info)

    return render_template('people_search.html', title="Lead Generator", business_data=[])

# Flask route for the existing dashboard
@app.route('/dashboard7')
def dashboard7():
    return render_template('dashboard.html', 
                           lead_count=session.get('lead_count', 0),
                           email_count=session.get('email_count', 0),
                           phone_count=session.get('phone_count', 0),
                           address_count=session.get('address_count', 0),
                           social_media_count=session.get('social_media_count', 0),
                           company_name_count=session.get('company_name_count', 0))


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




# Hot LEADS
from flask import Flask, render_template, request, session
import requests
from bs4 import BeautifulSoup
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import random
from fake_useragent import UserAgent

# Initialize UserAgent
ua = UserAgent()


# Function to clean and standardize text
def clean_text(text):
    if not text:
        return "N/A"
    text = BeautifulSoup(text, 'html.parser').get_text()  # Remove HTML tags
    text = text.strip()
    text = ' '.join(text.split())  # Normalize spaces
    return text

# Function to clean and format phone numbers
def clean_phone(phone):
    if not phone:
        return None

    # Remove unwanted words like "Phone", "Call", "Tel", or any non-digit characters (except for parentheses, dashes, and spaces)
    phone = re.sub(r'(\bPhone\b|\bCall\b|\bTel\b|[^\d\(\)\-\s])', '', phone)

    # Remove extra spaces and line breaks
    phone = re.sub(r'\s+', ' ', phone).strip()

    # Now clean the phone number format (only digits should remain)
    digits = re.sub(r'\D', '', phone)  # Keep only digits

    # Filter out numbers with only 1 or 2 digits, which are not valid phone numbers
    if len(digits) <= 2:
        return None

    # Validate and format phone numbers
    if len(digits) == 10:  # Standard 10-digit number
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    elif len(digits) == 11 and digits[0] == '1':  # US phone number starting with 1 (country code)
        return f"+1 ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
    
    return None

# Function to clean and standardize addresses
def clean_address(address):
    if not address:
        return "N/A"
    
    address = re.sub(r'\s+', ' ', address).strip()  # Normalize spaces
    if len(address) < 5 or not any(word in address.lower() for word in [
        "street", "road", "avenue", "drive", "lane", "boulevard", "court", "plaza", "terrace", "crescent"
    ]):
        return "N/A"
    
    return address

# Function to extract contact information from a webpage
def extract_contact_info(url):
    headers = {"User-Agent": ua.random}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract emails, phones, and addresses using regex
        email_pattern = r"([\w\.-]+@[\w\.-]+\.\w+)"
        phone_pattern = r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}"
        address_pattern = r"\d+\s[\w\s]+(?:St|Ave|Rd|Blvd|Ln|Terr|Pl)\.?"

        emails = list(set(re.findall(email_pattern, soup.get_text())))
        phones = list(set(re.findall(phone_pattern, soup.get_text())))
        addresses = list(set(re.findall(address_pattern, soup.get_text())))

        # Clean extracted data
        emails = [clean_text(email) for email in emails]
        phones = [clean_phone(phone) for phone in phones]
        addresses = [clean_address(address) for address in addresses]

        # Limit results to top 2 entries for each type
        contact_info = {
            "emails": emails[:2],
            "phone_numbers": [p for p in phones[:2] if p],  # Ensure phone numbers are not None
            "addresses": addresses[:2]
        }

        return contact_info

    except Exception as e:
        print(f"Error processing {url}: {e}")
        return {"emails": [], "phone_numbers": [], "addresses": []}

# Function to scrape results from Mojeek search engine
import time

# Function to scrape results from Mojeek search engine
def scrape_mojeek(query, num_results=30):
    base_url = "https://www.mojeek.com/search"
    results = []
    page = 1

    while len(results) < num_results:
        url = f"{base_url}?q={query.replace(' ', '+')}&page={page}"
        headers = {"User-Agent": ua.random}

        try:
            # Adding a slight delay between requests
            time.sleep(random.uniform(1, 2))  # Delay of 1 to 2 seconds between requests
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            search_results = soup.select("ul.results-standard li")
            for result in search_results:
                title_tag = result.select_one("a.title")
                link_tag = result.select_one("a.ob")
                description_tag = result.select_one("p.s")

                title = clean_text(title_tag.text if title_tag else "No title available")
                link = link_tag["href"] if link_tag else "No link available"
                description = clean_text(description_tag.text if description_tag else "No description available")

                results.append({
                    "title": title,
                    "link": link,
                    "description": description
                })

            if len(results) >= num_results:
                break

            page += 1

        except requests.exceptions.RequestException as e:
            print(f"Error fetching results: {e}")
            # You could also add retry logic here
            time.sleep(random.uniform(3, 5))  # Add longer wait time after an error
            continue

    return results[:num_results]


@app.route('/hot_leads', methods=['GET', 'POST'])
@login_required
def hot_leads():
    query = request.form.get('query', '')
    results = []
    email_count = 0
    phone_count = 0
    address_count = 0

    if query:
        raw_results = scrape_mojeek(query, num_results=30)

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(extract_contact_info, result['link']): result for result in raw_results}
            
            for future in as_completed(futures):
                result = futures[future]
                try:
                    contact_info = future.result()
                    results.append({**result, **contact_info})
                    email_count += len(contact_info['emails'])
                    phone_count += len(contact_info['phone_numbers'])
                    address_count += len(contact_info['addresses'])
                except Exception as e:
                    print(f"Error at {result['link']}: {e}")

        # Store everything needed for reuse
        session['results'] = results
        session['query'] = query  # Save the query
        session['email_count'] = email_count
        session['phone_count'] = phone_count
        session['address_count'] = address_count

    return render_template("hot_leads.html", results=results, query=query, datetime=datetime)


@app.route('/dashboard23')
def dashboard23():
    # Retrieve the counts stored in session
    email_count = session.get('email_count', 0)
    phone_count = session.get('phone_count', 0)
    address_count = session.get('address_count', 0)

    return render_template("dashboard.html", email_count=email_count, phone_count=phone_count, address_count=address_count)




# Lead Manager------------------------------------------------------------
@app.route('/lead_manager')
@login_required
def lead_manager():
    # Retrieve all data from the session
    results = session.get('results', [])
    query = session.get('query', '')
    email_count = session.get('email_count', 0)
    phone_count = session.get('phone_count', 0)
    address_count = session.get('address_count', 0)

    # Pass the same variables as hot_leads.html
    return render_template(
        "lead_manager.html",
        results=results,
        query=query,
        datetime=datetime,
        email_count=email_count,
        phone_count=phone_count,
        address_count=address_count
    )

# SESSION CLEAR



# SOCIAL MEDIA LEADS-----------------

import random
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from flask import Flask, render_template, request, redirect, url_for, session
from fake_useragent import UserAgent

# Initialize Flask app


# Create a user-agent manager instance for dynamic user-agent rotation
user_agents = UserAgent()

# Function to generate random headers and simulate human-like browsing
def get_random_headers():
    headers = {
        "User-Agent": user_agents.random,  # Randomized user agent from fake_useragent
        "Accept-Language": random.choice(["en-US", "en-GB", "en-CA"]),  # Randomize language
        "Connection": "keep-alive",  # Mimic human-like persistent connection
        "DNT": "1",  # Do Not Track
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Referer": "https://www.google.com",  # Randomized referer to simulate the flow of a human browsing
        "Upgrade-Insecure-Requests": "1",  # Simulate insecure request upgrade
    }
    return headers

# Function to perform the HTTP request with retry logic, randomized delays, and headers
def perform_http_request(url):
    headers = get_random_headers()

    session = requests.Session()
    retry_strategy = requests.adapters.Retry(total=3, backoff_factor=1)
    adapter = requests.adapters.HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    # Random sleep between 2-5 seconds before each request
    time.sleep(random.uniform(2, 5))

    try:
        response = session.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error during request to {url}: {e}")
        return None

# Function to scrape Bing search results using requests and BeautifulSoup
def scrape_bing_results(query):
    search_url = f"https://www.bing.com/search?q={query}"
    page_content = perform_http_request(search_url)

    if not page_content:
        return []

    soup = BeautifulSoup(page_content, 'html.parser')

    results = []

    for result in soup.find_all('li', class_='b_algo'):
        title = result.find('h2').get_text() if result.find('h2') else 'No title'
        link = result.find('a')['href'] if result.find('a') else 'No link'
        domain = urlparse(link).netloc
        description = result.find('p').get_text() if result.find('p') else 'No description'

        # Filter out "best", "directory", "list" keywords and trusted domains
        if "best" not in title.lower() and "directory" not in title.lower() and "list" not in title.lower():
            if "yelp.com" not in domain and "tripadvisor.com" not in domain:
                results.append({
                    'title': title,
                    'link': link,
                    'domain': domain,
                    'description': description
                })

    return results

# Function to validate URLs
def is_valid_url(url):
    parsed_url = urlparse(url)
    return parsed_url.scheme in ("http", "https")

# Function to extract contact information (emails, phone, etc.) from a given URL
def extract_contact_info(url):
    if not is_valid_url(url):
        return {"error": "Invalid URL"}

    page_content = perform_http_request(url)
    if not page_content:
        return {"error": "Unable to fetch page"}

    soup = BeautifulSoup(page_content, 'html.parser')

    # Regular expressions for extracting emails and phone numbers
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    phone_pattern = r'\+?[0-9.\-\(\) ]{7,}'
    social_media_domains = ["twitter.com", "facebook.com", "linkedin.com", "instagram.com"]

    emails = re.findall(email_pattern, soup.get_text())
    phone_numbers = re.findall(phone_pattern, soup.get_text())
    
    # Extract social media links
    social_media_links = []
    for link in soup.find_all('a', href=True):
        href = link['href']
        if any(domain in href for domain in social_media_domains):
            social_media_links.append(href)

    # Extract addresses using a simple pattern
    address_pattern = r'\d{1,5}\s\w+\s\w+'
    addresses = re.findall(address_pattern, soup.get_text())
    
    # Extract company name from the page title
    company_name = soup.title.string if soup.title else "N/A"
    
    return {
        "emails": emails,
        "phone_numbers": phone_numbers,
        "addresses": addresses,
        "social_media_links": social_media_links,
        "company_name": company_name,
        "domain": url
    }

# Flask route for contact finder page
@app.route('/social_media_leads', methods=['GET', 'POST'])
@login_required
def social_media_leads():
    if request.method == 'POST':
        industry = request.form.get('industry')
        location = request.form.get('location')
        
        if not industry or not location:
            return redirect(url_for('contact_finder'))  # Return to the form if fields are missing

        query = f"{industry} {location}"
        search_results = scrape_bing_results(query)

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

        return render_template('social_media_leads.html', title="Contact Finder", business_data=extracted_info)

    return render_template('social_media_leads.html', title="Contact Finder", business_data=[])

# Flask route for the dashboard page
@app.route('/dashboard2')
def dashboard2():
    return render_template('dashboard.html', 
                           lead_count=session.get('lead_count', 0),
                           email_count=session.get('email_count', 0),
                           phone_count=session.get('phone_count', 0),
                           address_count=session.get('address_count', 0),
                           social_media_count=session.get('social_media_count', 0),
                           company_name_count=session.get('company_name_count', 0))





#Email LEADS----------------------
import random
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from flask import Flask, render_template, request, redirect, url_for, session
from fake_useragent import UserAgent


# Create a user-agent manager instance for dynamic user-agent rotation
user_agents = UserAgent()

# Function to create randomized headers for HTTP requests
def create_random_headers():
    headers = {
        "User-Agent": user_agents.random,
        "Accept-Language": random.choice(["en-US", "en-GB", "en-CA"]),
        "Connection": "keep-alive",
        "DNT": "1",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Referer": "https://www.google.com",
        "Upgrade-Insecure-Requests": "1",
    }
    return headers

# Function to fetch content from a URL with retries and headers
def retrieve_content(url):
    headers = create_random_headers()

    session = requests.Session()
    retry_strategy = requests.adapters.Retry(total=3, backoff_factor=1)
    adapter = requests.adapters.HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    time.sleep(random.uniform(2, 5))

    try:
        response = session.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

# Function to parse search results from Bing
def parse_search_results(query):
    search_url = f"https://www.bing.com/search?q={query}"
    page_content = retrieve_content(search_url)

    if not page_content:
        return []

    soup = BeautifulSoup(page_content, 'html.parser')
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

# Function to validate URLs
def validate_url(url):
    parsed_url = urlparse(url)
    return parsed_url.scheme in ("http", "https")

# Function to extract information from a webpage
def gather_contact_info(url):
    if not validate_url(url):
        return {"error": "Invalid URL"}

    page_content = retrieve_content(url)
    if not page_content:
        return {"error": "Unable to fetch page"}

    soup = BeautifulSoup(page_content, 'html.parser')
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    phone_pattern = r'\+?[0-9.\-\(\) ]{7,}'
    social_media_domains = ["twitter.com", "facebook.com", "linkedin.com", "instagram.com"]

    emails = re.findall(email_pattern, soup.get_text())
    phone_numbers = re.findall(phone_pattern, soup.get_text())

    social_media_links = []
    for link in soup.find_all('a', href=True):
        href = link['href']
        if any(domain in href for domain in social_media_domains):
            social_media_links.append(href)

    address_pattern = r'\d{1,5}\s\w+\s\w+'
    addresses = re.findall(address_pattern, soup.get_text())
    company_name = soup.title.string if soup.title else "N/A"

    return {
        "emails": emails,
        "phone_numbers": phone_numbers,
        "addresses": addresses,
        "social_media_links": social_media_links,
        "company_name": company_name,
        "domain": url
    }

# Flask route for the lead-fetching feature
@app.route('/email_leads', methods=['GET', 'POST'])
@login_required
def email_leads():
    if request.method == 'POST':
        industry = request.form.get('industry')
        location = request.form.get('location')
        
        if not industry or not location:
            return redirect(url_for('lead_form_page'))

        query = f"{industry} {location}"
        search_results = parse_search_results(query)

        collected_data = []
        for result in search_results:
            contact_info = gather_contact_info(result['link'])
            if contact_info.get('company_name') and contact_info['company_name'] != "N/A":
                collected_data.append(contact_info)

        # Store leads data in session
        session['leads'] = collected_data
        session['lead_count'] = len(collected_data)
        session['email_count'] = sum(len(info.get('emails', [])) for info in collected_data)
        session['phone_count'] = sum(len(info.get('phone_numbers', [])) for info in collected_data)
        session['address_count'] = sum(len(info.get('addresses', [])) for info in collected_data)
        session['social_media_count'] = sum(len(info.get('social_media_links', [])) for info in collected_data)
        session['company_name_count'] = sum(1 for info in collected_data if info.get('company_name'))

        return render_template('email_leads.html', title="Lead Collector", business_data=collected_data)

    return render_template('email_leads.html', title="Lead Collector", business_data=[])

# Flask route for the dashboard
@app.route('/dashboard5')
def dashboard5():
    return render_template('dashboard.html', 
                           lead_count=session.get('lead_count', 0),
                           email_count=session.get('email_count', 0),
                           phone_count=session.get('phone_count', 0),
                           address_count=session.get('address_count', 0),
                           social_media_count=session.get('social_media_count', 0),
                           company_name_count=session.get('company_name_count', 0))



# PHONE LEADS---------------------------
import random
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from flask import Flask, render_template, request, redirect, url_for, session
from fake_useragent import UserAgent


# Create a user-agent manager instance for dynamic user-agent rotation
user_agents = UserAgent()

# Function to generate random headers and simulate human-like browsing
def generate_headers():
    headers = {
        "User-Agent": user_agents.random,
        "Accept-Language": random.choice(["en-US", "en-GB", "en-CA"]),
        "Connection": "keep-alive",
        "DNT": "1",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Referer": "https://www.google.com",
        "Upgrade-Insecure-Requests": "1",
    }
    return headers

# Function to handle HTTP requests with retry logic, randomized delays, and headers
def fetch_url_content(url):
    headers = generate_headers()

    session = requests.Session()
    retry_strategy = requests.adapters.Retry(total=3, backoff_factor=1)
    adapter = requests.adapters.HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    time.sleep(random.uniform(2, 5))

    try:
        response = session.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

# Function to scrape search engine results using BeautifulSoup
def search_results_scraper(query):
    search_url = f"https://www.bing.com/search?q={query}"
    page_content = fetch_url_content(search_url)

    if not page_content:
        return []

    soup = BeautifulSoup(page_content, 'html.parser')
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

# Function to check the validity of URLs
def check_url_validity(url):
    parsed_url = urlparse(url)
    return parsed_url.scheme in ("http", "https")

# Function to extract contact details from a webpage
def extract_lead_details(url):
    if not check_url_validity(url):
        return {"error": "Invalid URL"}

    page_content = fetch_url_content(url)
    if not page_content:
        return {"error": "Unable to fetch page"}

    soup = BeautifulSoup(page_content, 'html.parser')
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    phone_pattern = r'\+?[0-9.\-\(\) ]{7,}'
    social_media_domains = ["twitter.com", "facebook.com", "linkedin.com", "instagram.com"]

    emails = re.findall(email_pattern, soup.get_text())
    phone_numbers = re.findall(phone_pattern, soup.get_text())

    social_media_links = []
    for link in soup.find_all('a', href=True):
        href = link['href']
        if any(domain in href for domain in social_media_domains):
            social_media_links.append(href)

    address_pattern = r'\d{1,5}\s\w+\s\w+'
    addresses = re.findall(address_pattern, soup.get_text())
    company_name = soup.title.string if soup.title else "N/A"

    return {
        "emails": emails,
        "phone_numbers": phone_numbers,
        "addresses": addresses,
        "social_media_links": social_media_links,
        "company_name": company_name,
        "domain": url
    }

# Flask route for lead generation feature
@app.route('/phone_leads', methods=['GET', 'POST'])
@login_required
def phone_leads():
    if request.method == 'POST':
        industry = request.form.get('industry')
        location = request.form.get('location')
        
        if not industry or not location:
            return redirect(url_for('lead_generation_form'))

        query = f"{industry} {location}"
        search_results = search_results_scraper(query)

        lead_details = []
        for result in search_results:
            contact_info = extract_lead_details(result['link'])
            if contact_info.get('company_name') and contact_info['company_name'] != "N/A":
                lead_details.append(contact_info)

        # Store leads data in session
        session['leads'] = lead_details
        session['lead_count'] = len(lead_details)
        session['email_count'] = sum(len(info.get('emails', [])) for info in lead_details)
        session['phone_count'] = sum(len(info.get('phone_numbers', [])) for info in lead_details)
        session['address_count'] = sum(len(info.get('addresses', [])) for info in lead_details)
        session['social_media_count'] = sum(len(info.get('social_media_links', [])) for info in lead_details)
        session['company_name_count'] = sum(1 for info in lead_details if info.get('company_name'))

        return render_template('phone_leads.html', title="Lead Generator", business_data=lead_details)

    return render_template('phone_leads.html', title="Lead Generator", business_data=[])

# Flask route for the existing dashboard
@app.route('/dashboard4')
def dashboard4():
    return render_template('dashboard4.html', 
                           lead_count=session.get('lead_count', 0),
                           email_count=session.get('email_count', 0),
                           phone_count=session.get('phone_count', 0),
                           address_count=session.get('address_count', 0),
                           social_media_count=session.get('social_media_count', 0),
                           company_name_count=session.get('company_name_count', 0))









# ADDRESS LEADS----------------------------------------------
import random
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from flask import Flask, render_template, request, redirect, url_for, session
from fake_useragent import UserAgent

# Initialize Flask app

# Create a user-agent manager instance for dynamic user-agent rotation
user_agents = UserAgent()

# Function to generate headers for HTTP requests
def generate_headers():
    headers = {
        "User-Agent": user_agents.random,
        "Accept-Language": random.choice(["en-US", "en-GB", "en-CA"]),
        "Connection": "keep-alive",
        "DNT": "1",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Referer": "https://www.google.com",
        "Upgrade-Insecure-Requests": "1",
    }
    return headers

# Function to fetch content from URLs
def fetch_page_content(url):
    headers = generate_headers()

    session = requests.Session()
    retry_strategy = requests.adapters.Retry(total=3, backoff_factor=1)
    adapter = requests.adapters.HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    time.sleep(random.uniform(2, 5))

    try:
        response = session.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error while fetching {url}: {e}")
        return None

# Function to parse Bing search results
def parse_bing_results(query):
    search_url = f"https://www.bing.com/search?q={query}"
    page_content = fetch_page_content(search_url)

    if not page_content:
        return []

    soup = BeautifulSoup(page_content, 'html.parser')
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

# Function to validate a given URL
def validate_url_structure(url):
    parsed_url = urlparse(url)
    return parsed_url.scheme in ("http", "https")

# Function to extract contact data from pages
def extract_data(url):
    if not validate_url_structure(url):
        return {"error": "Invalid URL"}

    page_content = fetch_page_content(url)
    if not page_content:
        return {"error": "Unable to fetch page"}

    soup = BeautifulSoup(page_content, 'html.parser')
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    phone_pattern = r'\+?[0-9.\-\(\) ]{7,}'
    social_media_domains = ["twitter.com", "facebook.com", "linkedin.com", "instagram.com"]

    emails = re.findall(email_pattern, soup.get_text())
    phone_numbers = re.findall(phone_pattern, soup.get_text())

    social_media_links = []
    for link in soup.find_all('a', href=True):
        href = link['href']
        if any(domain in href for domain in social_media_domains):
            social_media_links.append(href)

    address_pattern = r'\d{1,5}\s\w+\s\w+'
    addresses = re.findall(address_pattern, soup.get_text())
    company_name = soup.title.string if soup.title else "N/A"

    return {
        "emails": emails,
        "phone_numbers": phone_numbers,
        "addresses": addresses,
        "social_media_links": social_media_links,
        "company_name": company_name,
        "domain": url
    }

# Flask route to handle lead collection
@app.route('/address_leads', methods=['GET', 'POST'])
@login_required
def address_leads():
    if request.method == 'POST':
        industry = request.form.get('industry')
        location = request.form.get('location')
        
        if not industry or not location:
            return redirect(url_for('lead_form_view'))

        query = f"{industry} {location}"
        search_results = parse_bing_results(query)

        lead_list = []
        for result in search_results:
            contact_data = extract_data(result['link'])
            if contact_data.get('company_name') and contact_data['company_name'] != "N/A":
                lead_list.append(contact_data)

        # Store leads data in session
        session['leads'] = lead_list
        session['lead_count'] = len(lead_list)
        session['email_count'] = sum(len(info.get('emails', [])) for info in lead_list)
        session['phone_count'] = sum(len(info.get('phone_numbers', [])) for info in lead_list)
        session['address_count'] = sum(len(info.get('addresses', [])) for info in lead_list)
        session['social_media_count'] = sum(len(info.get('social_media_links', [])) for info in lead_list)
        session['company_name_count'] = sum(1 for info in lead_list if info.get('company_name'))

        return render_template('address_leads.html', title="Lead Collection", business_data=lead_list)

    return render_template('address_leads.html', title="Lead Collection", business_data=[])

# Flask route for the dashboard
@app.route('/dashboard6')
def dashboard6():
    return render_template('dashboard.html', 
                           lead_count=session.get('lead_count', 0),
                           email_count=session.get('email_count', 0),
                           phone_count=session.get('phone_count', 0),
                           address_count=session.get('address_count', 0),
                           social_media_count=session.get('social_media_count', 0),
                           company_name_count=session.get('company_name_count', 0))







if __name__ == '__main__':
    app.run(threaded=True)
