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
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Load environment variables from .env file
load_dotenv()

class SeleniumManager:
    """Manages a single, reusable, logged-in Selenium browser session."""
    def __init__(self, debug: bool = False):
        self.username = os.getenv("LINKEDIN_USER")
        self.password = os.getenv("LINKEDIN_PASS")

        if not self.username or not self.password:
            raise ValueError("LINKEDIN_USER and LINKEDIN_PASS must be set in your .env file.")

        chrome_options = Options()
        if not debug:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        service = Service()
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        print("🚀 Headless browser session started.")
        self.login()

    def login(self):
        """Logs into LinkedIn using explicit waits."""
        print("🔐 Attempting to log into LinkedIn...")
        self.driver.get("https://www.linkedin.com/login")
        try:
            wait = WebDriverWait(self.driver, 10)
            username_field = wait.until(EC.visibility_of_element_located((By.ID, "username")))
            username_field.send_keys(self.username)
            self.driver.find_element(By.ID, "password").send_keys(self.password)
            self.driver.find_element(By.XPATH, '//button[@type="submit"]').click()
            wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".global-nav")))
            print("✅ Login successful!")
        except Exception as e:
            print(f"❌ Login failed. Error: {e}")
            self.close()
            raise

    def _parse_follower_text(self, text: str) -> Optional[int]:
        """
        Parses text like "1.2K followers" or "100M followers" into an integer.
        """
        text = text.lower().replace('followers', '').strip()
        text = text.replace(',', '')
        
        multiplier = 1
        if 'k' in text:
            multiplier = 1000
            text = text.replace('k', '')
        elif 'm' in text:
            multiplier = 1000000
            text = text.replace('m', '')
        
        try:
            number = float(text)
            return int(number * multiplier)
        except ValueError:
            return None

    def get_followers(self, company_url: str) -> Optional[int]:
        """
        Navigates to a company page and scrapes the follower count, handling
        abbreviations like 'K' for thousands and 'M' for millions.
        """
        if not company_url: return None
        try:
            self.driver.get(company_url)

            wait = WebDriverWait(self.driver, 10)
            wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "org-top-card-summary-info-list__info-item")))
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            text_to_parse = None
            
            # Priority 1 (Logged-in): Find the <a> tag with an aria-label containing "followers".
            follower_link = soup.find('a', attrs={'aria-label': re.compile(r'followers', re.IGNORECASE)})
            
            if follower_link:
                text_to_parse = follower_link['aria-label']
            else:
                # Fallback (Logged-out): Find the specific info div that contains the word "followers".
                follower_div = soup.find(
                    'div',
                    class_='org-top-card-summary-info-list__info-item',
                    string=re.compile(r'followers', re.IGNORECASE)
                )
                if follower_div:
                    text_to_parse = follower_div.get_text()

            # If text was found, parse it using our helper method
            if text_to_parse:
                return self._parse_follower_text(text_to_parse)
            
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