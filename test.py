# LEAD GENERATION

# List of user-agents
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0"
]

def get_random_user_agent():
    return random.choice(user_agents)

# Function to perform a DuckDuckGo search and get URLs
def duckduckgo_search(query):
    search_url = f"https://duckduckgo.com/html/?q={query}"
    headers = {
        "User-Agent": get_random_user_agent(),
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://duckduckgo.com",
        "DNT": "1",  # Do Not Track Request Header
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
    }

    try:
        response = requests.get(search_url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        results = []
        for result in soup.find_all('a', {'class': 'result__a'}):  # Corrected class for DuckDuckGo result links
            title = result.text.strip()
            link = result['href']
            # Filtering and ensuring we get valid links
            if link.startswith('/l/') or link.startswith('/?q='):
                link = urljoin("https://duckduckgo.com", link)  # Resolving relative URLs to full URLs
            results.append({'title': title, 'link': link})

        return results
    except requests.exceptions.RequestException as e:
        print(f"Error during search: {e}")
        return []

def random_delay():
    time.sleep(random.uniform(1.5, 3.0))  # Random delay between 1.5 to 3 seconds

# Helper functions for extracting information
def extract_info(page_tree, base_url):
    info = {
        'emails': set(),
        'phone_numbers': set(),
        'addresses': set(),
        'social_media': set(),
        'company_name': None,
    }
    # Patterns for extracting data
    email_pattern = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zAZ0-9.-]+\.[a-zA-Z]{2,}")
    phone_pattern = re.compile(r"\+?\d[\d\s\-\(\)]{7,}\d")
    address_patterns = [
        re.compile(pattern) for pattern in [
            r"\d{1,5}\s[\w\s.,-]{1,100},?\s[A-Z]{2}\s\d{5}",
            r"\d{1,5}\s[\w\s.,-]{1,100},?\s[\w\s.,-]{1,100},?\s[A-Z]{2}\s\d{5}",
            r"\d+\s[\w\s.,-]+\s[\w\s.,-]+,\s\w+\s[A-Z]{2}\s\d{5}",
        ]
    ]
    social_media_domains = {"facebook.com", "twitter.com", "linkedin.com", "instagram.com"}

    page_text = page_tree.body.text()

    # Extract emails, phone numbers, and addresses from text
    info['emails'].update(email_pattern.findall(page_text))
    info['phone_numbers'].update(phone_pattern.findall(page_text)[:2])
    for pattern in address_patterns:
        info['addresses'].update(pattern.findall(page_text))

    # Extract emails from 'mailto' links
    for node in page_tree.css('a[href^=mailto]'):
        email = node.attributes.get('href', '').split(':')[1].split('?')[0]
        info['emails'].add(email)

    # Extract social media links
    for node in page_tree.css('a[href]'):
        href = node.attributes.get('href', '')
        if href and any(domain in href for domain in social_media_domains):
            info['social_media'].add(urljoin(base_url, href))

    # Extract company name from structured data or meta tags
    for node in page_tree.css("script[type='application/ld+json']"):
        try:
            structured_data = json.loads(node.text())
            if "name" in structured_data:
                info['company_name'] = structured_data["name"]
                break
        except json.JSONDecodeError:
            continue

    if not info['company_name']:
        meta_name = page_tree.css_first('meta[property="og:site_name"]')
        if meta_name:
            info['company_name'] = meta_name.attributes.get('content', '')

    # Fallback to domain name if company name is still not found
    if not info['company_name']:
        domain = urlparse(base_url).netloc.split('.')
        if len(domain) > 1:
            business_name = domain[0].replace('www', '').replace('-', ' ').replace('_', ' ').title()
            if business_name.lower() not in ('top', '10', 'forbes', 'yelp', 'houzz', 'tripadvisor', 'angieslist', 'yellowpages', 'bbb'):
                info['company_name'] = business_name

    # Ensure all sets are converted to lists before returning
    return {k: list(v) if isinstance(v, set) else v for k, v in info.items()}

# Define the function to fetch page content
def fetch_page_content(url, headers):
    try:
        random_delay()
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            page_tree = HTMLParser(response.text)  # Use selectolax's HTMLParser
            return page_tree
        else:
            print(f"Failed to retrieve {url} with status code {response.status_code}")
            return None
    except Exception as e:
        print(f"Error fetching content from {url}: {e}")
        return None

# Lead generator page route
@app.route('/leads-generator')
@login_required
def leads_generator():
    # Retrieve session data to display
    leads = session.get('leads', [])
    lead_count = session.get('lead_count', 0)
    email_count = session.get('email_count', 0)
    phone_count = session.get('phone_count', 0)
    address_count = session.get('address_count', 0)
    social_media_count = session.get('social_media_count', 0)
    company_name_count = session.get('company_name_count', 0)

    # Render the template and pass data
    return render_template(
        'leads_generator.html',
        title="Leads Generator",
        leads=leads,
        lead_count=lead_count,
        email_count=email_count,
        phone_count=phone_count,
        address_count=address_count,
        social_media_count=social_media_count,
        company_name_count=company_name_count
    )

# Main search route
@app.route('/search', methods=['POST'])
@login_required
def search():
    query = request.form.get('business_type')
    if not query:
        return redirect(url_for('leads_generator'))

    search_results = duckduckgo_search(query)
    leads = []
    headers = {
        "User-Agent": get_random_user_agent(),
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://duckduckgo.com",
        "DNT": "1",  # Do Not Track Request Header
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
    }

    # Using ThreadPoolExecutor to fetch data in parallel
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {}  # Using a dictionary to store futures and their corresponding link_node
        for result in search_results:
            link = result['link']
            future = executor.submit(fetch_page_content, link, headers)
            futures[future] = link  # Store link in the dictionary with future as the key

    # Handle the results
    for future in as_completed(futures):
        page_content = future.result()
        link = futures[future]  # Retrieve the associated link for each future
        if page_content:
            base_url = urljoin(link, '/')
            info = extract_info(page_content, base_url)
            leads.append({
                'link': link,
                'info': info
            })

    # Store leads data in session
    session['leads'] = leads  # Store the leads in session
    session['lead_count'] = len(leads)
    session['email_count'] = sum(len(lead['info'].get('emails', [])) for lead in leads)
    session['phone_count'] = sum(len(lead['info'].get('phone_numbers', [])) for lead in leads)
    session['address_count'] = sum(len(lead['info'].get('addresses', [])) for lead in leads)
    session['social_media_count'] = sum(len(lead['info'].get('social_media', [])) for lead in leads)
    session['company_name_count'] = sum(1 for lead in leads if lead['info'].get('company_name'))

    # Redirect to the leads generator page after updating session
    return redirect(url_for('leads_generator'))


