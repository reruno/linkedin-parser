from bs4 import BeautifulSoup
import pprint
# Import necessary types for hinting
from typing import List, Dict, Optional, TypedDict

# Define a specific type for our job data dictionary for clarity
class JobData(TypedDict):
    title: Optional[str]
    company: Optional[str]
    location: Optional[str]
    url: Optional[str]
    date_posted_text: Optional[str]
    date_posted_iso: Optional[str]
    company_logo_url: Optional[str]

def parse_linkedin_jobs(html_content: str) -> List[JobData]:
    """
    Parses the HTML content of a LinkedIn job search results page.

    Args:
        html_content (str): A string containing the raw HTML of the page.

    Returns:
        List[JobData]: A list of dictionaries, where each dictionary contains the
                       details of a single job posting. Returns an empty list
                       if no jobs are found or in case of an error.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    job_cards = soup.find_all('div', class_='base-search-card')
    
    extracted_jobs: List[JobData] = []

    for card in job_cards:
        # Extract Job Title
        title_element = card.find('h3', class_='base-search-card__title')
        title = title_element.get_text(strip=True) if title_element else None

        # Extract Company Name
        company_element = card.find('h4', class_='base-search-card__subtitle')
        company = None
        if company_element and company_element.find('a'):
            company = company_element.find('a').get_text(strip=True)

        # Extract Location
        location_element = card.find('span', class_='job-search-card__location')
        location = location_element.get_text(strip=True) if location_element else None

        # Extract Job URL
        url_element = card.find('a', class_='base-card__full-link')
        url = url_element['href'] if url_element else None
        
        # Extract Date Posted
        date_element = card.find('time', class_='job-search-card__listdate')
        date_posted_text = date_element.get_text(strip=True) if date_element else None
        date_posted_iso = date_element['datetime'] if date_element else None

        # Extract Company Logo URL
        logo_element = card.find('img', class_='artdeco-entity-image')
        company_logo_url = None
        if logo_element:
            company_logo_url = logo_element.get('data-delayed-url', logo_element.get('src'))

        # Create the dictionary that conforms to the JobData TypedDict
        job_data: JobData = {
            'title': title,
            'company': company,
            'location': location,
            'url': url,
            'date_posted_text': date_posted_text,
            'date_posted_iso': date_posted_iso,
            'company_logo_url': company_logo_url,
        }

        extracted_jobs.append(job_data)
        
    return extracted_jobs

# --- Example Usage ---
# Paste the HTML content you provided into this multiline string
html_from_linkedin = """
<body><li>
        
    

    
    
    
      <div class="base-card relative w-full hover:no-underline focus:no-underline
        base-card--link
         base-search-card base-search-card--link job-search-card" data-entity-urn="urn:li:jobPosting:4305720538" data-impression-id="jobs-search-result-0" data-reference-id="dXbebcy5Zc8hoaoltSvOaA==" data-tracking-id="JkxHhZA8S6oCIfrPrmN6Gg==" data-column="1" data-row="1">
        

        <a class="base-card__full-link absolute top-0 right-0 bottom-0 left-0 p-0 z-[2] outline-offset-[4px]" href="https://pl.linkedin.com/jobs/view/819-senior-golang-developer-short-term-at-intetics-4305720538?position=1&amp;pageNum=0&amp;refId=dXbebcy5Zc8hoaoltSvOaA%3D%3D&amp;trackingId=JkxHhZA8S6oCIfrPrmN6Gg%3D%3D" data-tracking-control-name="public_jobs_jserp-result_search-card" data-tracking-client-ingraph="" data-tracking-will-navigate="">
          
          <span class="sr-only">
              
        
        819 | Senior Golang Developer (Short term)
      
      
          </span>
        </a>

      
        
    <div class="search-entity-media">
        
      <img class="artdeco-entity-image artdeco-entity-image--square-4
          " data-delayed-url="https://media.licdn.com/dms/image/v2/D4D0BAQGPo4xi1y3FaA/company-logo_100_100/B4DZc10aZbGUAQ-/0/1748954621937/intetics_logo?e=1762992000&amp;v=beta&amp;t=MTOFD7589bcvwhWl2TQGPFtEjcAcdFl9HJRBy7DxCc0" data-ghost-classes="artdeco-entity-image--ghost" data-ghost-url="https://static.licdn.com/aero-v1/sc/h/6puxblwmhnodu6fjircz4dn4h" alt="">
  
    </div>
  

        <div class="base-search-card__info">
          <h3 class="base-search-card__title">
            
        819 | Senior Golang Developer (Short term)
      
          </h3>

            <h4 class="base-search-card__subtitle">
              
          <a class="hidden-nested-link" data-tracking-client-ingraph="" data-tracking-control-name="public_jobs_jserp-result_job-search-card-subtitle" data-tracking-will-navigate="" href="https://www.linkedin.com/company/intetics?trk=public_jobs_jserp-result_job-search-card-subtitle">
            Intetics
          </a>
      
            </h4>

            <div class="base-search-card__metadata">
              
          <span class="job-search-card__location">
            Poland
          </span>

        
    
    
    
    

      <div class="job-posting-benefits text-sm">
        <icon class="job-posting-benefits__icon" data-delayed-url="https://static.licdn.com/aero-v1/sc/h/8zmuwb93gzlb935fk4ao4z779" data-svg-class-name="job-posting-benefits__icon-svg"></icon>
        <span class="job-posting-benefits__text">
          Be an early applicant
        </span>
      </div>
  

          <time class="job-search-card__listdate" datetime="2025-09-26">
            

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    

    
    
    
    
    
    
    
    
    
    
    
    
    
    

      2 weeks ago
  
          </time>

          <span class="job-search-card__easy-apply-label job-search-card__easy-apply-label--with-middot">
            Apply Now
          </span>
      
            </div>
        </div>
      
    
      </div>
  
  
  
  
      </li>
      <li>
        
    

    
    
    
      <div class="base-card relative w-full hover:no-underline focus:no-underline
        base-card--link
         base-search-card base-search-card--link job-search-card" data-entity-urn="urn:li:jobPosting:4270690853" data-impression-id="jobs-search-result-1" data-reference-id="dXbebcy5Zc8hoaoltSvOaA==" data-tracking-id="yCY5vpAiP2eLE/AHTjNOmA==" data-column="1" data-row="2">
        

        <a class="base-card__full-link absolute top-0 right-0 bottom-0 left-0 p-0 z-[2] outline-offset-[4px]" href="https://pl.linkedin.com/jobs/view/backend-engineer-senior-go-nord-account-team-at-nord-security-4270690853?position=2&amp;pageNum=0&amp;refId=dXbebcy5Zc8hoaoltSvOaA%3D%3D&amp;trackingId=yCY5vpAiP2eLE%2FAHTjNOmA%3D%3D" data-tracking-control-name="public_jobs_jserp-result_search-card" data-tracking-client-ingraph="" data-tracking-will-navigate="">
          
          <span class="sr-only">
              
        
        Backend Engineer | Senior | Go | Nord Account Team
      
      
          </span>
        </a>

      
        
    <div class="search-entity-media">
        
      <img class="artdeco-entity-image artdeco-entity-image--square-4
          " data-delayed-url="https://media.licdn.com/dms/image/v2/C4E0BAQE7Fs46KFoosw/company-logo_100_100/company-logo_100_100/0/1630627290687/nordsecurity_logo?e=1762992000&amp;v=beta&amp;t=oyJ6Y9xinqgUhUveQUk1qS6gta22emU9dWWQz9DWq3U" data-ghost-classes="artdeco-entity-image--ghost" data-ghost-url="https://static.licdn.com/aero-v1/sc/h/6puxblwmhnodu6fjircz4dn4h" alt="">
  
    </div>
  

        <div class="base-search-card__info">
          <h3 class="base-search-card__title">
            
        Backend Engineer | Senior | Go | Nord Account Team
      
          </h3>

            <h4 class="base-search-card__subtitle">
              
          <a class="hidden-nested-link" data-tracking-client-ingraph="" data-tracking-control-name="public_jobs_jserp-result_job-search-card-subtitle" data-tracking-will-navigate="" href="https://www.linkedin.com/company/nordsecurity?trk=public_jobs_jserp-result_job-search-card-subtitle">
            Nord Security
          </a>
      
            </h4>

            <div class="base-search-card__metadata">
              
          <span class="job-search-card__location">
            Warsaw, Mazowieckie, Poland
          </span>

        
    
    
    
    

      <div class="job-posting-benefits text-sm">
        <icon class="job-posting-benefits__icon" data-delayed-url="https://static.licdn.com/aero-v1/sc/h/8zmuwb93gzlb935fk4ao4z779" data-svg-class-name="job-posting-benefits__icon-svg"></icon>
        <span class="job-posting-benefits__text">
          Be an early applicant
        </span>
      </div>
  

          <time class="job-search-card__listdate" datetime="2025-07-21">
            

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    

    
    
    
    
    
    
    
    
    
    
    
    
    
    

      2 months ago
  
          </time>

          <span class="job-search-card__easy-apply-label job-search-card__easy-apply-label--with-middot">
            Apply Now
          </span>
      
            </div>
        </div>
      
    
      </div>
  
  
  
  
      </li>
</body>
"""

# Call the function and pretty-print the result
parsed_data = parse_linkedin_jobs(html_from_linkedin)
pprint.pprint(parsed_data)