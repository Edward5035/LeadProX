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

