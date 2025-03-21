import requests                          # Fetches the web page content
from bs4 import BeautifulSoup            # Parses HTML content
import re                                # Regular expressions for extracting emails, phone numbers, and addresses
import csv                               # Saves extracted data to a CSV file
import argparse                          # Parses command-line arguments
from typing import List, Dict, Optional  # Type hinting for better code readability

# Regular expression patterns for extracting contact details
EMAIL_PATTERN = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"  # Matches email addresses
PHONE_PATTERN = r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}"              # Matches phone numbers in various formats
ADDRESS_PATTERN = r"\d{1,5}\s[\w\s]+(?:St|Street|Ave|Avenue|Rd|Road|Blvd|Boulevard)[^,]*,\s[\w\s]+,\s\w{2,}\s\d{5}(?:-\d{4})?"
# Matches US-style addresses with street, city, state, and zip code

def scrape_url(url: str) -> str:
    """Fetch HTML content from the provided URL."""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}  # Mimic a browser request
        response = requests.get(url, headers=headers, timeout=10)  # Fetch the page with a timeout of 10 seconds
        response.raise_for_status()  # Raise an error for HTTP errors (4xx, 5xx)
        return response.text  # Return the raw HTML content of the page
    except requests.RequestException as e:
        print(f"Error fetching URL: {e}")  # Print error message if the request fails
        return ""  # Return an empty string if fetching fails

def extract_company_details(html: str, url: str) -> List[Dict[str, Optional[str]]]:
    """Extract company details, emails, phone numbers, and addresses from the HTML content."""
    soup = BeautifulSoup(html, "html.parser")  # Parse the HTML content
    text = soup.get_text(separator=" ")  # Extract all visible text from the page

    # Extract company name from various sources (title, h1, meta description, or URL)
    company_name = None
    if soup.title and soup.title.string:
        company_name = soup.title.string.strip()  # Use the page title if available
    elif soup.find("h1"):
        company_name = soup.find("h1").get_text().strip()  # Use the first <h1> tag if available
    elif soup.find("meta", {"name": "description"}):
        company_name = soup.find("meta", {"name": "description"})["content"].strip()  # Use meta description if available
    if not company_name and url:
        company_name = url.split("//")[-1].split("/")[0].replace("www.", "")  # Extract domain name as a fallback

    # Extract emails, phone numbers, and addresses using regular expressions
    emails = set(re.findall(EMAIL_PATTERN, text))  # Find all unique email addresses
    phones = set(re.findall(PHONE_PATTERN, text))  # Find all unique phone numbers
    addresses = set(re.findall(ADDRESS_PATTERN, text))  # Find all unique addresses

    # Store extracted contacts in a list of dictionaries, avoiding duplicates
    contacts = []
    seen_entries = set()  # Keeps track of unique records to prevent duplication

    # Add emails to the contact list
    for email in emails:
        entry = (company_name, email, None, None)  # Define a unique entry
        if entry not in seen_entries:
            contacts.append({"company_name": company_name, "email": email, "phone": None, "address": None})
            seen_entries.add(entry)

    # Add phone numbers to the contact list
    for phone in phones:
        entry = (company_name, None, phone, None)  # Define a unique entry
        if entry not in seen_entries:
            if not emails or all(c["email"] for c in contacts):
                contacts.append({"company_name": company_name, "email": None, "phone": phone, "address": None})
            else:
                for contact in contacts:
                    if contact["phone"] is None and contact["email"]:  # Add phone to existing contact if possible
                        contact["phone"] = phone
                        break
            seen_entries.add(entry)

    # Add addresses to the contact list
    for address in addresses:
        entry = (company_name, None, None, address)  # Define a unique entry
        if entry not in seen_entries:
            if not contacts:
                contacts.append({"company_name": company_name, "email": None, "phone": None, "address": address})
            else:
                for contact in contacts:
                    if contact["address"] is None:  # Add address to an existing entry if possible
                        contact["address"] = address
                        break
            seen_entries.add(entry)

    # If no contact details were found, return at least the company name
    return contacts if contacts else [{"company_name": company_name, "email": None, "phone": None, "address": None}]

def save_to_csv(contacts: List[Dict[str, Optional[str]]], filename: str = "leads.csv"):
    """Save extracted contact details to a CSV file."""
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["company_name", "email", "phone", "address"])  # Define CSV column headers
        writer.writeheader()  # Write the header row
        writer.writerows(contacts)  # Write contact details row by row
    print(f"\nResults saved: {len(contacts)} entries written to '{filename}'")  # Print success message

def main():
    """Main function to run the web scraper."""
    parser = argparse.ArgumentParser(description="Lead generation scraper for company details and contacts.")
    parser.add_argument("--url", required=True, help="URL to scrape (e.g., https://example.com/contact)")  # Accepts a URL input
    args = parser.parse_args()  # Parse command-line arguments

    url = args.url
    print(f"\n=== Scraping {url} for company details and leads ===")  # Inform the user about the scraping process

    html = scrape_url(url)  # Fetch the page content
    if not html:
        print("Failed to retrieve content. Exiting.")  # Exit if the request failed
        return

    contacts = extract_company_details(html, url)  # Extract company details from the HTML
    if not contacts:
        print("No data found.")  # Exit if no data was found
        return

    # Display extracted details in a structured format
    print("\n=== Extracted Data ===")
    for i, contact in enumerate(contacts, 1):
        print(f"Entry {i}:")
        print(f"  Company: {contact['company_name'] or 'Not Found'}")
        print(f"  Email:   {contact['email'] or 'Not Found'}")
        print(f"  Phone:   {contact['phone'] or 'Not Found'}")
        print(f"  Address: {contact['address'] or 'Not Found'}")
        print()

    # Save extracted data to a CSV file
    save_to_csv(contacts)

if __name__ == "__main__":
    main()  # Execute the script when run from the command line
