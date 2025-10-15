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
from selenium.common.exceptions import TimeoutException

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
        """
        Logs into LinkedIn using explicit waits and a retry mechanism.
        It will attempt to log in up to 3 times on failure.
        """
        max_retries = 3
        for attempt in range(max_retries):
            try:
                print(f"🔐 Attempting to log into LinkedIn (Attempt {attempt + 1}/{max_retries})...")
                self.driver.get("https://www.linkedin.com/login")
                
                # Wait up to 15 seconds for the username field to be visible
                wait = WebDriverWait(self.driver, 15)
                username_field = wait.until(EC.visibility_of_element_located((By.ID, "username")))
                
                # Enter credentials and click sign in
                username_field.send_keys(self.username)
                self.driver.find_element(By.ID, "password").send_keys(self.password)
                self.driver.find_element(By.XPATH, '//button[@type="submit"]').click()

                # Wait for the main navigation to appear, which confirms a successful login
                wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".global-nav")))
                
                # If we reach here, login was successful
                print("✅ Login successful!")
                return # Exit the function on success

            except Exception as e:
                print(f"❌ Login attempt {attempt + 1} failed. Error: {e}")
                if attempt < max_retries - 1:
                    print("    - Retrying in 3 seconds...")
                    time.sleep(3) # Wait before the next attempt
        
        # If the loop completes without a successful login, raise an error.
        print("❌ All login attempts failed.")
        self.close()
        raise Exception("Could not log into LinkedIn after multiple attempts.")

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
        Navigates to a company page and scrapes the follower count. It will retry
        up to 3 times on failure, especially for long loading times.
        """
        if not company_url:
            return None

        max_retries = 3
        for attempt in range(max_retries):
            try:
                self.driver.get(company_url)

                # Wait up to 15 seconds for the key element to appear
                wait = WebDriverWait(self.driver, 15)
                wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "org-top-card-summary-info-list__info-item")))
                
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                text_to_parse = None
                
                # Priority 1 (Logged-in): Find the <a> tag with an aria-label containing "followers"
                follower_link = soup.find('a', attrs={'aria-label': re.compile(r'followers', re.IGNORECASE)})
                
                if follower_link:
                    text_to_parse = follower_link['aria-label']
                else:
                    # Fallback (Logged-out): Find the specific info div
                    follower_div = soup.find(
                        'div',
                        class_='org-top-card-summary-info-list__info-item',
                        string=re.compile(r'followers', re.IGNORECASE)
                    )
                    if follower_div:
                        text_to_parse = follower_div.get_text()

                # If text was found, parse it and return successfully
                if text_to_parse:
                    followers = self._parse_follower_text(text_to_parse)
                    if followers is not None:
                        return followers # Success! Exit the function.
                
                # If the element was not found, it's a parsing failure. We'll let it retry.
                print(f"    - Could not find follower element on attempt {attempt + 1}.")

            except TimeoutException:
                print(f"    - Page timed out on attempt {attempt + 1}/{max_retries} for {company_url}.")
            except Exception as e:
                print(f"    - An unexpected error occurred on attempt {attempt + 1}/{max_retries}: {e}")

            # If this wasn't the last attempt, wait before retrying
            if attempt < max_retries - 1:
                print("    - Retrying...")
                time.sleep(2) # A short delay between retries

        # If all retries fail, return None
        print(f"    - All retries failed for {company_url}.")
        return None
    
    def close(self):
        """Closes the browser session."""
        if self.driver:
            self.driver.quit()
            print("\nBrowser session closed.")