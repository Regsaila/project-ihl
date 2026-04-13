import requests
from dotenv import load_dotenv
from pathlib import Path
import os

load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")

APP_ID = os.getenv("ADZUNA_APP_ID")
APP_KEY = os.getenv("ADZUNA_APP_KEY")

def scrape(job_title: str, location: str = "Toronto", pages: int = 3):
    print(f"\nSearching for '{job_title}' jobs in '{location}'...")

    jobs = []

    for page in range(1, pages + 1):
        url = f"https://api.adzuna.com/v1/api/jobs/ca/search/{page}"
        params = {
            "app_id": APP_ID,
            "app_key": APP_KEY,
            "what": job_title,
            "where": location,
            "results_per_page": 20,
        }
        response = requests.get(url, params=params)

        if response.status_code != 200:
            print(f"API error on page {page}: {response.status_code}")
            break

        results = response.json().get("results", [])

        for job in results:
            jobs.append({
                "title": job.get("title", "N/A"),
                "company": job.get("company", {}).get("display_name", "N/A"),
                "location": job.get("location", {}).get("display_name", "N/A"),
                "description": job.get("description", "N/A"),
                "url": job.get("redirect_url", "N/A"),
                "date": job.get("created", "N/A"),
                "salary": job.get("salary_min", "N/A")
            })

    print(f"Found {len(jobs)} jobs\n")
    return jobs


if __name__ == "__main__":
    results = scrape("IT Technician", "Toronto")
    for job in results:
        print(f"{job['title']} at {job['company']}")
        print(f"{job['location']}")
        print(f"{job['url']}")
        print("-" * 50)