# -*- coding: utf-8 -*-

"""
A script to fetch and parse job listings from LinkedIn's guest-facing API.
"""

# --- 1. Dependencies ---
# Make sure to install these libraries first:
# pip install requests beautifulsoup4
import requests
from bs4 import BeautifulSoup
from typing import List, Optional, TypedDict
# --- 4. Export Functions ---
import csv
import pandas as pd

# --- 2. Type Definitions ---
# Defines the structure for a single job posting's data for clarity and type checking.
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
    start: int = 0,
    f_TPR: str = ""
) -> List[JobData]:
    """
    Fetches job listings from LinkedIn by making an API request and then parses the HTML response.

    Args:
        keywords (str): The job title or keyword to search for (e.g., "Python Developer").
        location (str): The geographical location for the job search (e.g., "Poland").
        start (int): The starting point for pagination, typically in increments of 25.
        f_TPR (str): Time-posting range filter. Accepts "r86400" (last 24h),
                     "r604800" (last week), or "r2592000" (last month).

    Returns:
        A list of job data dictionaries. Returns an empty list if the request fails.
    """
    base_url = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
    params = {
        'keywords': keywords,
        'location': location,
        'start': start,
        'f_TPR': f_TPR
    }

    print(f"🚀 Fetching jobs from LinkedIn with params: {params}")
    try:
        # It's good practice to include a user-agent header to mimic a browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(base_url, params=params, headers=headers, timeout=10)
        response.raise_for_status()  # Raises an exception for bad status codes (4xx or 5xx)
    except requests.exceptions.RequestException as e:
        print(f"❌ An error occurred during the request: {e}")
        return []

    # Directly parse the response text and return the result
    return parse_linkedin_jobs(response.text)


def parse_linkedin_jobs(html_content: str) -> List[JobData]:
    """
    Parses the raw HTML content from a LinkedIn job search response.

    Args:
        html_content (str): The HTML string to be parsed.

    Returns:
        A list of job data dictionaries, with each dictionary representing one job posting.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    job_cards = soup.find_all('div', class_='base-search-card')
    extracted_jobs: List[JobData] = []

    for card in job_cards:
        # Extract data for each field, handling cases where an element might be missing
        title_element = card.find('h3', class_='base-search-card__title')
        title = title_element.get_text(strip=True) if title_element else None
        
        company_element = card.find('h4', class_='base-search-card__subtitle')
        company_name = None
        company_url = None
        if company_element and company_element.find('a'):
            company_name = company_element.find('a').get_text(strip=True)
            company_url = company_element.find('a')['href']
            
        location_element = card.find('span', class_='job-search-card__location')
        location = location_element.get_text(strip=True) if location_element else None
        
        url_element = card.find('a', class_='base-card__full-link')
        url = url_element['href'] if url_element else None
        
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



def export_to_csv(data: List[JobData], filename: str):
    """
    Exports a list of job data dictionaries to a CSV file.

    Args:
        data (List[JobData]): The list of jobs to export.
        filename (str): The desired name of the output file (without extension).
    """
    if not data:
        print("⚠️ No data to export.")
        return

    # Ensure the filename ends with .csv
    csv_filename = f"{filename}.csv"
    
    # Get the headers from the keys of the first dictionary
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
    """
    Exports a list of job data dictionaries to an Excel file (.xlsx).

    Args:
        data (List[JobData]): The list of jobs to export.
        filename (str): The desired name of the output file (without extension).
    """
    if not data:
        print("⚠️ No data to export.")
        return

    # Ensure the filename ends with .xlsx
    excel_filename = f"{filename}.xlsx"
    
    try:
        # Convert the list of dictionaries to a pandas DataFrame
        df = pd.DataFrame.from_dict(data)
        # Write the DataFrame to an Excel file
        df.to_excel(excel_filename, index=False)
        print(f"✅ Data successfully exported to {excel_filename}")
    except Exception as e:
        print(f"❌ Error exporting to Excel: {e}")

# --- 5. Example Usage ---
if __name__ == "__main__":
    search_keywords = "Golang"
    search_location = "Poland"
    time_filter = "r604800"  # Past Week
    
    jobs_list = fetch_linkedin_jobs(
        keywords=search_keywords,
        location=search_location,
        f_TPR=time_filter
    )

    if jobs_list:
        print(f"\n✅ Successfully found {len(jobs_list)} jobs.")
        
        # Define a base filename for the output files
        output_filename = f"linkedin_jobs_{search_keywords}_{search_location}".replace(" ", "_")
        
        # Export the data to both formats
        export_to_csv(jobs_list, output_filename)
        export_to_excel(jobs_list, output_filename)
        
    else:
        print("\n❌ No jobs found. This could be due to no results or the request being blocked by LinkedIn.")