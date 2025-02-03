
import requests
import random
import time
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
from collections import Counter
from flask import Flask, render_template, request

# Initialize Flask


# Create a random user agent for each request
user_agents = UserAgent()

# Create a persistent session to simulate real user behavior using `requests.Session()`
http_session = requests.Session()

# Define stopwords directly (reusing your original stopwords)
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

# Function to perform HTTP request with random headers using `requests.Session()`
def perform_http_request(url):
    headers = {
        "User-Agent": user_agents.random,  # Randomize User-Agent
        "Accept-Language": random.choice(["en-US", "en-GB", "en-CA"]),
        "Connection": "keep-alive",
        "DNT": "1",  # Do Not Track header
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
    }

    # Add a random delay between requests to simulate human-like behavior
    time.sleep(random.uniform(2, 10))  # Simulate human-like delay (2 to 10 seconds)

    try:
        # Use `http_session` to make the GET request, not Flask's session
        response = http_session.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Will raise an error for bad status codes
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

# Function to gather business data and handle pagination
def gather_business_data(industry, location, max_pages=5):
    query = f"{industry} in {location}"
    base_url = f"https://www.bing.com/search?q={query}&first="

    scraped_data = []

    for page_num in range(max_pages):
        url = f"{base_url}{page_num * 10 + 1}"  # Adjust the page number for pagination
        print(f"Scraping page {page_num + 1}: {url}")
        
        page_content = perform_http_request(url)
        if not page_content:
            break

        soup = BeautifulSoup(page_content, 'html.parser')

        # Extract the business listings
        business_list = soup.select('.b_algo')

        for business in business_list:
            name = business.find('h2').text
            website = business.find('a')['href'] if business.find('a') else "N/A"

            # Skip if no valid website
            if website == "N/A":
                continue

            # Extract and rank keywords from the homepage
            keywords = fetch_keywords(website)

            # Calculate keyword percentages
            total_keywords = sum([freq for _, freq in keywords])
            keyword_percentages = [(keyword, freq / total_keywords * 100) for keyword, freq in keywords]

            # Append the extracted data
            scraped_data.append({
                "name": name,
                "website": website,
                "keywords": keyword_percentages
            })

    return scraped_data

# Flask route for SEO Rocket interface
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

