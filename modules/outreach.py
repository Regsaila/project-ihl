import requests
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from dotenv import load_dotenv
import anthropic

load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")

HUNTER_API_KEY = os.getenv("HUNTER_API_KEY")
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def find_recruiter_email(company_name: str) -> dict:
    print(f"🔎 Looking up recruiter at {company_name}...")

    params = {
        "company": company_name,
        "api_key": HUNTER_API_KEY
    }
    response = requests.get("https://api.hunter.io/v2/domain-search", params=params)

    if response.status_code != 200:
        print(f"⚠️ Hunter API error: {response.status_code}")
        return {}

    data = response.json().get("data", {})
    domain = data.get("domain", "")
    emails = data.get("emails", [])

    if not emails:
        print(f"⚠️ No emails found for {company_name}")
        return {}

    # Skip if company is clearly not Canadian
    non_canadian_tlds = [".co.uk", ".com.au", ".co.in", ".de", ".fr"]
    if any(tld in domain for tld in non_canadian_tlds):
        print(f"⚠️ Skipping {company_name} — domain '{domain}' doesn't appear Canadian")
        return {}

    # Prioritize HR/recruiter emails
    priority_keywords = ["hr", "recruit", "talent", "hiring", "people"]
    for email in emails:
        position = (email.get("position") or "").lower()
        if any(kw in position for kw in priority_keywords):
            return {
                "email": email.get("value"),
                "name": f"{email.get('first_name', '')} {email.get('last_name', '')}".strip(),
                "position": email.get("position", "Hiring Manager")
            }

    # Fall back to first email
    first = emails[0]
    return {
        "email": first.get("value"),
        "name": f"{first.get('first_name', '')} {first.get('last_name', '')}".strip(),
        "position": first.get("position", "Hiring Manager")
    }


def write_outreach_email(job: dict, recruiter: dict) -> dict:
    print(f"✍️  Writing outreach email for {job['company']}...")

    recruiter_name = recruiter.get("name") or "Hiring Manager"

    prompt = f"""Write a short, genuine, and personalized cold outreach email from a job applicant to a recruiter.

Applicant: Ali Saifee
- Final semester Network Engineering student at Sheridan College
- IT Technician experience at Universal Data Supplies (Toronto) and Saif Tech (Kuwait)
- Skills: Cisco, AWS, Azure, Active Directory, Python, Windows/Linux
- AWS Academy Certified

Recruiter Name: {recruiter_name}
Company: {job['company']}
Job Title: {job['title']}
Job URL: {job['url']}

Write a 3 paragraph email:
1. Who Ali is and why he's reaching out
2. Why he's specifically interested in this company and role
3. Call to action — asking for a quick chat or to review his application

Keep it human, confident, and concise. No fluff. Sign off as Ali Saifee.

Respond in this exact format:
SUBJECT: [subject line]
BODY:
[email body]
"""

    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )

    response = message.content[0].text
    subject = ""
    body = ""

    if "SUBJECT:" in response and "BODY:" in response:
        parts = response.split("BODY:")
        subject = parts[0].replace("SUBJECT:", "").strip()
        body = parts[1].strip()

    return {"subject": subject, "body": body}


def send_email(to_email: str, subject: str, body: str) -> bool:
    print(f"📧 Sending email to {to_email}...")
    try:
        msg = MIMEMultipart()
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, to_email, msg.as_string())

        print(f"✅ Email sent to {to_email}")
        return True
    except Exception as e:
        print(f"⚠️ Failed to send email: {e}")
        return False


def outreach(job: dict) -> bool:
    recruiter = find_recruiter_email(job["company"])
    if not recruiter:
        return False

    email_content = write_outreach_email(job, recruiter)
    if not email_content["subject"]:
        return False

    print(f"\n📨 Email Preview:")
    print(f"To: {recruiter['email']} ({recruiter['name']})")
    print(f"Subject: {email_content['subject']}")
    print(f"Body:\n{email_content['body']}\n")

    return send_email(recruiter["email"], email_content["subject"], email_content["body"])


if __name__ == "__main__":
    test_job = {
        "title": "IT Support Technician",
        "company": "Excis Compliance",
        "url": "https://www.adzuna.ca/details/5672481175"
    }
    outreach(test_job)