# -*- coding: utf-8 -*-
import os
import re
import time
from typing import Optional

from bs4 import BeautifulSoup
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time 
import re
from typing import Optional
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# Load environment variables from .env file
load_dotenv()

class SeleniumManager:
    """Manages a single, reusable, logged-in Selenium browser session."""
    def __init__(self):
        self.username = os.getenv("LINKEDIN_USER")
        self.password = os.getenv("LINKEDIN_PASS")

        if not self.username or not self.password:
            raise ValueError("LINKEDIN_USER and LINKEDIN_PASS must be set in your .env file.")

        chrome_options = Options()
        # chrome_options.add_argument("--headless")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        service = Service()
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        print("🚀 Headless browser session started.")
        self.login()

    def login(self):
        """Logs into LinkedIn using credentials from the .env file."""
        print("🔐 Attempting to log into LinkedIn...")
        self.driver.get("https://www.linkedin.com/login")
        time.sleep(3) # Give login page time to load

        try:
            self.driver.find_element(By.ID, "username").send_keys(self.username)
            self.driver.find_element(By.ID, "password").send_keys(self.password)
            self.driver.find_element(By.XPATH, '//button[@type="submit"]').click()
            time.sleep(5) # Wait for login to process and redirect
            # A simple check to see if the URL changed from /login
            if "login" in self.driver.current_url:
                raise Exception("Login failed, still on login page.")
            print("✅ Login successful!")
        except Exception as e:
            print(f"❌ Login failed. Error: {e}")
            self.close()
            raise

    def get_followers(self, company_url: str) -> Optional[int]:
        """
        Navigates to a company page and scrapes the follower count.
        This method is updated to use a more reliable selector for logged-in sessions.
        """
        if not company_url: return None
        try:
            self.driver.get(company_url)
            # time.sleep(1)

            wait = WebDriverWait(self.driver, 1)
            wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "feed-shared-carousel")))
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            text_to_parse = None
            
            # --- NEW, MORE RELIABLE LOGIC ---
            # Priority 1: Find the <a> tag with an aria-label containing "followers". This is very specific.
            follower_link = soup.find('a', attrs={'aria-label': re.compile(r'followers', re.IGNORECASE)})
            
            if follower_link:
                # If found, get the text directly from the aria-label attribute
                text_to_parse = follower_link['aria-label']
            else:
                # Fallback: If not logged in, find the original h3 element
                h3_element = soup.find('h3', class_='org-top-card-summary-info-list__info-item')
                if h3_element:
                    text_to_parse = h3_element.get_text()
            
            # If we found text from either method, parse it
            if text_to_parse:
                match = re.search(r'([\d,]+)\s+followers', text_to_parse)
                if match:
                    return int(match.group(1).replace(',', ''))
            
            # If neither element was found or the text didn't match
            print(f"    - Could not find follower element on page: {company_url}")
            return None

        except Exception as e:
            print(f"    - An error occurred while getting followers for {company_url}. Error: {e}")
            return None
    
    def close(self):
        """Closes the browser session."""
        if self.driver:
            self.driver.quit()
            print("\nBrowser session closed.")