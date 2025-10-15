# -*- coding: utf-8 -*-

"""
A script to fetch, parse, enrich with follower counts, and export job listings
from LinkedIn's guest-facing API, reusing a single Selenium session.
"""

# --- 1. Dependencies ---
# pip install requests beautifulsoup4 pandas openpyxl selenium
import requests
from bs4 import BeautifulSoup
from typing import List, Optional, TypedDict
import csv
import pandas as pd
import math
import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium_manager import SeleniumManager

# --- 2. Type Definitions ---
class JobData(TypedDict):
    title: Optional[str]
    company_name: Optional[str]
    company_url: Optional[str]
    company_followers_number: Optional[int] # New field for followers
    location: Optional[str]
    url: Optional[str]
    date_posted_text: Optional[str]
    date_posted_iso: Optional[str]
    company_logo_url: Optional[str]

# --- 4. Core Functions ---
def enrich_jobs_with_followers(jobs_list: List[JobData], selenium_manager: SeleniumManager) -> List[JobData]:
    """
    Enriches job data with company follower counts using a reusable Selenium session.
    """
    company_followers_cache = {}
    unique_company_urls = {job['company_url'] for job in jobs_list if job['company_url']}

    print(f"\n🔎 Found {len(unique_company_urls)} unique companies. Fetching follower counts...")

    for i, url in enumerate(unique_company_urls):
        print(f"  - Scraping ({i+1}/{len(unique_company_urls)}): {url}")
        followers = selenium_manager.get_followers(url)
        company_followers_cache[url] = followers
        time.sleep(0.2) # Be respectful between requests

    for job in jobs_list:
        job['company_followers_number'] = company_followers_cache.get(job['company_url'])

    print("✅ Enrichment complete.")
    return jobs_list


def fetch_linkedin_jobs(keywords: str, location: str, limit: int = 50, f_TPR: str = "") -> List[JobData]:
    """Fetches job listings from LinkedIn using requests."""
    all_jobs: List[JobData] = []
    pages_to_fetch = math.ceil(limit / 25)
    print(f"🎯 Goal: Fetch {limit} jobs via API. This will require up to {pages_to_fetch} pages.")
    # (The rest of this function is unchanged)
    for page_num in range(pages_to_fetch):
        start = page_num * 25
        base_url = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
        params = {'keywords': keywords, 'location': location, 'start': start, 'f_TPR': f_TPR}
        print(f"📄 Fetching page {page_num + 1} (starting at job {start})...")
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            response = requests.get(base_url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"❌ An error occurred during API request on page {page_num + 1}: {e}")
            break
        newly_parsed_jobs = parse_linkedin_jobs(response.text)
        if not newly_parsed_jobs:
            print("⏹️ No more jobs found from API. Stopping.")
            break
        all_jobs.extend(newly_parsed_jobs)
        if len(all_jobs) >= limit:
            break
    return all_jobs[:limit]


def parse_linkedin_jobs(html_content: str) -> List[JobData]:
    """Parses the raw HTML from the job search API response."""
    soup = BeautifulSoup(html_content, 'html.parser')
    job_cards = soup.find_all('div', class_='base-search-card')
    extracted_jobs: List[JobData] = []
    for card in job_cards:
        # (Parsing logic is mostly the same, just adding the new field as None)
        title_element = card.find('h3', class_='base-search-card__title')
        title = title_element.get_text(strip=True) if title_element else None
        company_element = card.find('h4', class_='base-search-card__subtitle')
        company_name, company_url = None, None
        if company_element and company_element.find('a'):
            link_element = company_element.find('a')
            company_name = link_element.get_text(strip=True)
            company_url = link_element.get('href')
        location_element = card.find('span', class_='job-search-card__location')
        location = location_element.get_text(strip=True) if location_element else None
        url_element = card.find('a', class_='base-card__full-link')
        url = url_element.get('href') if url_element else None
        date_element = card.find('time', class_='job-search-card__listdate')
        date_posted_text = date_element.get_text(strip=True) if date_element else None
        date_posted_iso = date_element.get('datetime') if date_element else None
        logo_element = card.find('img', class_='artdeco-entity-image')
        company_logo_url = logo_element.get('data-delayed-url', logo_element.get('src')) if logo_element else None
        job_data: JobData = {
            'title': title, 'company_name': company_name, 'company_url': company_url,
            'company_followers_number': None, # Initialize as None
            'location': location, 'url': url, 'date_posted_text': date_posted_text,
            'date_posted_iso': date_posted_iso, 'company_logo_url': company_logo_url,
        }
        extracted_jobs.append(job_data)
    return extracted_jobs

# --- 5. Export Functions ---
def export_to_csv(data: List[JobData], filename: str):
    """Exports a list of job data dictionaries to a CSV file."""
    if not data: return
    csv_filename = f"{filename}.csv"
    headers = data[0].keys()
    try:
        with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(data)
        print(f"✅ Data successfully exported to {csv_filename}")
    except IOError as e: print(f"❌ Error exporting to CSV: {e}")

def export_to_excel(data: List[JobData], filename: str):
    """Exports a list of job data dictionaries to an Excel file."""
    if not data: return
    excel_filename = f"{filename}.xlsx"
    try:
        pd.DataFrame.from_dict(data).to_excel(excel_filename, index=False)
        print(f"✅ Data successfully exported to {excel_filename}")
    except Exception as e: print(f"❌ Error exporting to Excel: {e}")

# --- 6. Main Execution ---
if __name__ == "__main__":
    selenium_manager = None
    try:
        # --- Search Parameters ---
        search_keywords = "Javascript"
        search_location = "Poland"
        time_filter = "r86400"  # Past 24 hours
        job_limit = 3

        # Step 1: Fetch initial job data using requests
        jobs_list = fetch_linkedin_jobs(
            keywords=search_keywords,
            location=search_location,
            limit=job_limit,
            f_TPR=time_filter
        )

        if jobs_list:
            # Step 2: Initialize Selenium and enrich data with followers
            selenium_manager = SeleniumManager()
            enriched_jobs = enrich_jobs_with_followers(jobs_list, selenium_manager)

            # Step 3: Export the final enriched data
            print(f"\n✅ Successfully found and processed {len(enriched_jobs)} jobs.")
            output_filename = f"linkedin_jobs_{search_keywords}_{search_location}".replace(" ", "_")
            export_to_csv(enriched_jobs, output_filename)
            export_to_excel(enriched_jobs, output_filename)
        else:
            print("\n❌ No jobs found.")
    finally:
        # Step 4: Ensure the browser session is always closed
        if selenium_manager:
            selenium_manager.close()