
import time
from flask import Flask, render_template
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
        else:
            business_data = []  # No data to scrape if either is empty

    # Render the template with the scraped data
    return render_template('leadfinder.html', business_data=business_data, industry=industry, location=location)



