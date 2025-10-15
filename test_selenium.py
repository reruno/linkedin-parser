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
from dotenv import load_dotenv
from selenium_manager import SeleniumManager

if __name__ == "__main__":
    # Define the company page you want to scrape
    target_url = "https://uk.linkedin.com/school/calyptus-web3/?trk=public_jobs_jserp-result_job-search-card-subtitle"
    target_url = "https://www.linkedin.com/company/solhelix?trk=public_jobs_jserp-result_job-search-card-subtitle"
    manager = None
    try:
        # 1. Create the manager (this also starts the browser and logs in)
        manager = SeleniumManager(debug=True)
        
        # 2. Get the follower count
        follower_count = manager.get_followers(target_url)

        # 3. Print the final result
        if follower_count is not None:
            print(f"\n📈 Result: The company has {follower_count} followers.")
        else:
            print("\n❌ Could not retrieve the follower count.")
        time.sleep(1000)
    finally:
        # 4. Ensure the browser is always closed
        if manager:
            manager.close()
