import anthropic
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

RESUME = """
Ali Saifee
aliasgershaherawala@gmail.com | +1(437)5661613 | Mississauga, ON
linkedin.com/in/ali-saifee-860224211/

SUMMARY
Networking student and IT technician with hands-on experience in network infrastructure, hardware support, and cloud technologies. Seeking an entry-level IT technician/admin role to apply skills in routing, switching, and system administration.

SKILLS
- Technical: Windows, MacOS, Linux, Cisco routers & switches, server setup, cabling, CCTV, Office 365, Google Workspace, AWS, Microsoft Azure
- Programming: PowerShell, Bash, Python, Java, web development, MySQL, MongoDB
- Professional: Customer Service, Project management, IT asset management, process optimization

EXPERIENCE
IT Technician | Universal Data Supplies | Mississauga, ON | 05/2024 - 09/2024
- Delivered troubleshooting for hardware, software, and network issues
- Assisted with Active Directory user management, password resets, and system updates
- Configured and maintained desktops, laptops, and peripherals
- Managed product listings and inventory leading to 65% increase in productivity

Assistant IT Technician | Saif Tech | Kuwait | 07/2019 - 03/2023
- Planned and installed structured cabling for offices and server rooms
- Set up routers, switches, and networking equipment for LAN/WAN connections
- Configured and installed CCTV systems with network integration
- Assisted with server room hardware installation and cable management

EDUCATION
Sheridan College | Network Engineering | Expected: 12/2026

CERTIFICATIONS
AWS Academy Graduate - AWS Academy Cloud Developing | Amazon Web Services | Apr 2025
"""

def tailor_resume(job: dict) -> dict:
    print(f"✍️  Tailoring resume for: {job['title']} at {job['company']}...")

    prompt = f"""You are an expert resume writer. Given the job posting below and the candidate's resume, do two things:

1. Write a tailored resume summary (3-4 sentences) that matches the job requirements
2. Write a short cover letter (3 paragraphs) personalized for this specific role and company

Job Title: {job['title']}
Company: {job['company']}
Location: {job['location']}
Job Description: {job['description']}

Candidate Resume:
{RESUME}

Respond in this exact format:
SUMMARY:
[tailored summary here]

COVER LETTER:
[cover letter here]
"""

    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )

    response = message.content[0].text

    # Parse the response
    summary = ""
    cover_letter = ""

    if "SUMMARY:" in response and "COVER LETTER:" in response:
        parts = response.split("COVER LETTER:")
        summary = parts[0].replace("SUMMARY:", "").strip()
        cover_letter = parts[1].strip()

    return {
        "title": job["title"],
        "company": job["company"],
        "url": job["url"],
        "tailored_summary": summary,
        "cover_letter": cover_letter
    }


if __name__ == "__main__":
    test_job = {
        "title": "IT Support Technician",
        "company": "Excis Compliance Ltd",
        "location": "Toronto, ON",
        "description": "Looking for an IT support technician with experience in hardware troubleshooting, Active Directory, networking, and Windows administration.",
        "url": "https://example.com"
    }

    result = tailor_resume(test_job)
    print("\n📄 TAILORED SUMMARY:")
    print(result["tailored_summary"])
    print("\n📝 COVER LETTER:")
    print(result["cover_letter"])