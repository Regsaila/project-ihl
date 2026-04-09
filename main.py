from modules.scraper import scrape
from modules.tailor import tailor_resume
from modules.outreach import outreach
from modules.database import init_db, save_job, mark_applied, get_pending_jobs

def is_relevant_job(job: dict) -> bool:
    title = job["title"].lower()
    
    it_keywords = ["it", "network", "tech", "support", "helpdesk", "help desk", 
                   "sysadmin", "system", "desktop", "deskside", "infrastructure",
                   "cloud", "devops", "engineer", "administrator", "analyst", "specialist"]
    
    reject_keywords = ["senior", "sr.", "lead", "manager", "director", "nurse", 
                       "doctor", "chiropodist", "orthopedist", "financial", "legal",
                       "bilingual", "lawyer", "contractor", "footcare", "film"]
    
    if any(kw in title for kw in reject_keywords):
        return False
        
    if not any(kw in title for kw in it_keywords):
        return False
    
    return True

# -- Config --
JOB_TITLES = [
    "IT Technician",
    "Network Administrator",
    "IT Support",
    "Junior Network Engineer"
]
LOCATION = "Toronto"
DRY_RUN = True  # Set to False when ready to actually send

def run():
    print("Job Hunter Agent Starting...\n")
    init_db()

    all_jobs = []
    for title in JOB_TITLES:
        jobs = scrape(title, LOCATION)
        all_jobs.extend(jobs)

    print(f"\nTotal jobs scraped: {len(all_jobs)}")
    
    all_jobs = [job for job in all_jobs if is_relevant_job(job)]
    print(f"Relevant jobs after filtering: {len(all_jobs)}")

    new_jobs = []
    for job in all_jobs:
        is_new = save_job(job)
        if is_new:
            new_jobs.append(job)

    print(f"New jobs found: {len(new_jobs)}")

    if not new_jobs:
        print("No new jobs found. Try again later.")
        return

    for job in new_jobs:
        print(f"\n{'='*60}")
        print(f"Processing: {job['title']} at {job['company']}")
        print(f"{'='*60}")

        tailored = tailor_resume(job)
        print(f"\nTailored Summary:\n{tailored['tailored_summary']}")

        if DRY_RUN:
            print("DRY RUN - email not sent")
            sent = False
        else:
            sent = outreach(job)

        if sent:
            mark_applied(job["url"])
            print(f"Applied and emailed for: {job['title']} at {job['company']}")
        else:
            print(f"Could not send outreach for: {job['title']} at {job['company']}")

    print(f"\nDone! Processed {len(new_jobs)} new jobs.")

if __name__ == "__main__":
    run()