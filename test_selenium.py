# -*- coding: utf-8 -*-

"""
A script that uses Selenium to scrape a LinkedIn company page
and extract the number of followers.
"""

# --- 1. Dependencies ---
# Make sure to install these libraries first:
# pip install selenium beautifulsoup4
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from typing import Optional
import re
import time
# --- 2. Core Function ---
def get_linkedin_followers(url: str) -> Optional[int]:
    """
    Launches a headless browser, navigates to a LinkedIn company URL,
    parses the HTML, and returns the number of followers as an integer.

    Args:
        url (str): The target LinkedIn company URL to scrape.

    Returns:
        An integer representing the number of followers, or None if it
        could not be found or an error occurred.
    """
    # --- Setup Chrome Options for headless browsing ---
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Run without opening a browser window
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    # --- Initialize WebDriver ---
    service = Service()
    driver = None
    followers_count = None

    print(f"🚀 Launching headless browser to fetch: {url}")

    try:
        # Create a new instance of the Chrome driver
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.get(url)
        print("✅ Navigation successful! Parsing page source...")

        # --- Get Page Source and Parse for Followers ---
        html_content = driver.page_source
        soup = BeautifulSoup(html_content, 'html.parser')

        # Find the h3 tag containing the follower count
        h3_element = soup.find('h3', class_='top-card-layout__first-subline')
        
        if h3_element:
            full_text = h3_element.get_text(strip=True)
            
            # Use regex to find the number preceding the word "followers"
            match = re.search(r'([\d,]+)\s+followers', full_text)
            
            if match:
                # Extract the matched string (e.g., "85,739")
                followers_str = match.group(1)
                
                # Remove commas and convert to an integer
                followers_count = int(followers_str.replace(',', ''))
                print(f"✅ Found follower count: {followers_count}")
        time.sleep(3000)
    except Exception as e:
        print(f"❌ An error occurred: {e}")
        return None  # Return None on error

    finally:
        # --- Important: Clean up and close the browser ---
        if driver:
            driver.quit()
            print("\nBrowser closed.")

    return followers_count

# --- 3. Script Execution ---
if __name__ == "__main__":
    target_url = "https://sg.linkedin.com/company/shijigroup?trk=public_jobs_jserp-result_job-search-card-subtitle"
    target_url = "https://uk.linkedin.com/school/calyptus-web3/?trk=public_jobs_jserp-result_job-search-card-subtitle"
    
    # Call the function to get the follower count
    follower_count = get_linkedin_followers(target_url)

    # Check the result and print it
    if follower_count is not None:
        print(f"\n📈 Final Result: The company has {follower_count} followers.")
    else:
        print("\n❌ Could not retrieve the follower count.")