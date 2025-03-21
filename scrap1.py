import requests
from bs4 import BeautifulSoup
import re
import csv
import argparse
from typing import List, Dict, Optional

# Regex patterns for validation
EMAIL_PATTERN = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
PHONE_PATTERN = r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}"
ADDRESS_PATTERN = r"\d{1,5}\s[\w\s]+(?:St|Street|Ave|Avenue|Rd|Road|Blvd|Boulevard)[^,]*,\s[\w\s]+,\s\w{2,}\s\d{5}(?:-\d{4})?"

def scrape_url(url: str) -> str:
    """Fetch HTML content from the provided URL."""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching URL: {e}")
        return ""

def extract_company_details(html: str, url: str) -> List[Dict[str, Optional[str]]]:
    """Extract company details and contacts from HTML."""
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(separator=" ")

    # Extract company name
    company_name = None
    if soup.title and soup.title.string:
        company_name = soup.title.string.strip()
    elif soup.find("h1"):
        company_name = soup.find("h1").get_text().strip()
    elif soup.find("meta", {"name": "description"}):
        company_name = soup.find("meta", {"name": "description"})["content"].strip()
    if not company_name and url:
        company_name = url.split("//")[-1].split("/")[0].replace("www.", "")

    # Extract contacts and addresses
    emails = set(re.findall(EMAIL_PATTERN, text))
    phones = set(re.findall(PHONE_PATTERN, text))
    addresses = set(re.findall(ADDRESS_PATTERN, text))

    # Build deduplicated contact entries
    contacts = []
    seen_entries = set()

    for email in emails:
        entry = (company_name, email, None, None)
        if entry not in seen_entries:
            contacts.append({"company_name": company_name, "email": email, "phone": None, "address": None})
            seen_entries.add(entry)

    for phone in phones:
        entry = (company_name, None, phone, None)
        if entry not in seen_entries:
            if not emails or all(c["email"] for c in contacts):
                contacts.append({"company_name": company_name, "email": None, "phone": phone, "address": None})
            else:
                for contact in contacts:
                    if contact["phone"] is None and contact["email"]:
                        contact["phone"] = phone
                        break
            seen_entries.add(entry)

    for address in addresses:
        entry = (company_name, None, None, address)
        if entry not in seen_entries:
            if not contacts:
                contacts.append({"company_name": company_name, "email": None, "phone": None, "address": address})
            else:
                for contact in contacts:
                    if contact["address"] is None:
                        contact["address"] = address
                        break
            seen_entries.add(entry)

    return contacts if contacts else [{"company_name": company_name, "email": None, "phone": None, "address": None}]

def save_to_csv(contacts: List[Dict[str, Optional[str]]], filename: str = "leads.csv"):
    """Save extracted details to a CSV file."""
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["company_name", "email", "phone", "address"])
        writer.writeheader()
        writer.writerows(contacts)
    print(f"\nResults saved: {len(contacts)} entries written to '{filename}'")

def main():
    """Main function to run the scraper."""
    parser = argparse.ArgumentParser(description="Lead generation scraper for company details and contacts.")
    parser.add_argument("--url", required=True, help="URL to scrape (e.g., https://example.com/contact)")
    args = parser.parse_args()

    url = args.url
    print(f"\n=== Scraping {url} for company details and leads ===")

    html = scrape_url(url)
    if not html:
        print("Failed to retrieve content. Exiting.")
        return

    contacts = extract_company_details(html, url)
    if not contacts:
        print("No data found.")
        return

    # Display results with improved formatting
    print("\n=== Extracted Data ===")
    for i, contact in enumerate(contacts, 1):
        print(f"Entry {i}:")
        print(f"  Company: {contact['company_name'] or 'Not Found'}")
        print(f"  Email:   {contact['email'] or 'Not Found'}")
        print(f"  Phone:   {contact['phone'] or 'Not Found'}")
        print(f"  Address: {contact['address'] or 'Not Found'}")
        print()

    # Save to CSV
    save_to_csv(contacts)

if __name__ == "__main__":
    main()