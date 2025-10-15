# -*- coding: utf-8 -*-

"""
A script to fetch, parse, and export a specified number of job listings
from LinkedIn's guest-facing API.
"""

# --- 1. Dependencies ---
# pip install requests beautifulsoup4 pandas openpyxl
import requests
from bs4 import BeautifulSoup
from typing import List, Optional, TypedDict
import csv
import pandas as pd
import math

# --- 2. Type Definitions ---
class JobData(TypedDict):
    title: Optional[str]
    company_name: Optional[str]
    company_url: Optional[str]
    location: Optional[str]
    url: Optional[str]
    date_posted_text: Optional[str]
    date_posted_iso: Optional[str]
    company_logo_url: Optional[str]


# --- 3. Core Functions ---
def fetch_linkedin_jobs(
    keywords: str,
    location: str,
    limit: int = 50,
    f_TPR: str = ""
) -> List[JobData]:
    """
    Fetches job listings from LinkedIn up to a specified limit by handling pagination.

    Args:
        keywords (str): The job title or keyword to search for.
        location (str): The geographical location for the job search.
        limit (int): The total number of jobs to fetch.
        f_TPR (str): Time-posting range filter.

    Returns:
        A list of job data dictionaries up to the specified limit.
    """
    all_jobs: List[JobData] = []
    
    # Calculate the number of pages to fetch
    pages_to_fetch = math.ceil(limit / 25)
    print(f"🎯 Goal: Fetch {limit} jobs. This will require up to {pages_to_fetch} pages.")

    for page_num in range(pages_to_fetch):
        start = page_num * 25
        
        base_url = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
        params = {
            'keywords': keywords,
            'location': location,
            'start': start,
            'f_TPR': f_TPR
        }

        print(f"📄 Fetching page {page_num + 1} (starting at job {start})...")
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(base_url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"❌ An error occurred during the request on page {page_num + 1}: {e}")
            break # Stop fetching if a request fails

        newly_parsed_jobs = parse_linkedin_jobs(response.text)

        if not newly_parsed_jobs:
            print("⏹️ No more jobs found. Stopping.")
            break # Stop if a page returns no jobs

        all_jobs.extend(newly_parsed_jobs)

        if len(all_jobs) >= limit:
            break # Stop once we've collected enough jobs

    # Return the list, sliced to the exact limit requested
    return all_jobs[:limit]


def parse_linkedin_jobs(html_content: str) -> List[JobData]:
    """
    Parses the raw HTML content from a LinkedIn job search response.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    job_cards = soup.find_all('div', class_='base-search-card')
    extracted_jobs: List[JobData] = []

    for card in job_cards:
        title_element = card.find('h3', class_='base-search-card__title')
        title = title_element.get_text(strip=True) if title_element else None
        
        company_element = card.find('h4', class_='base-search-card__subtitle')
        company_name = None
        company_url = None
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
        company_logo_url = None
        if logo_element:
            company_logo_url = logo_element.get('data-delayed-url', logo_element.get('src'))
            
        job_data: JobData = {
            'title': title,
            'company_name': company_name,
            'company_url': company_url,
            'location': location,
            'url': url,
            'date_posted_text': date_posted_text,
            'date_posted_iso': date_posted_iso,
            'company_logo_url': company_logo_url,
        }
        extracted_jobs.append(job_data)
        
    return extracted_jobs

# --- 4. Export Functions ---
def export_to_csv(data: List[JobData], filename: str):
    """Exports a list of job data dictionaries to a CSV file."""
    if not data:
        print("⚠️ No data to export.")
        return
    csv_filename = f"{filename}.csv"
    headers = data[0].keys()
    try:
        with open(csv_filename, 'w', newline='', encoding='utf-8') as output_file:
            writer = csv.DictWriter(output_file, fieldnames=headers)
            writer.writeheader()
            writer.writerows(data)
        print(f"✅ Data successfully exported to {csv_filename}")
    except IOError as e:
        print(f"❌ Error exporting to CSV: {e}")

def export_to_excel(data: List[JobData], filename: str):
    """Exports a list of job data dictionaries to an Excel file (.xlsx)."""
    if not data:
        print("⚠️ No data to export.")
        return
    excel_filename = f"{filename}.xlsx"
    try:
        df = pd.DataFrame.from_dict(data)
        df.to_excel(excel_filename, index=False)
        print(f"✅ Data successfully exported to {excel_filename}")
    except Exception as e:
        print(f"❌ Error exporting to Excel: {e}")

# --- 5. Example Usage ---
if __name__ == "__main__":
    # --- Search Parameters ---
    search_keywords = "Javascript"
    search_location = "Poland"
    time_filter = "r86400"  # Past Month
    job_limit = 100            # Set your desired limit here

    jobs_list = fetch_linkedin_jobs(
        keywords=search_keywords,
        location=search_location,
        limit=job_limit,
        f_TPR=time_filter
    )

    if jobs_list:
        print(f"\n✅ Successfully found and parsed {len(jobs_list)} jobs.")
        
        output_filename = f"linkedin_jobs_{search_keywords}_{search_location}".replace(" ", "_")
        
        export_to_csv(jobs_list, output_filename)
        export_to_excel(jobs_list, output_filename)
        
    else:
        print("\n❌ No jobs found.")