import re  # Import the regular expression module for pattern matching
import csv  # Import the CSV module for handling CSV file operations
import argparse  # Import argparse for command-line argument parsing
from selenium import webdriver  # Import Selenium WebDriver for web automation
from selenium.webdriver.chrome.service import Service  # Import Chrome Service for managing WebDriver
from webdriver_manager.chrome import ChromeDriverManager  # Import WebDriver Manager for automatic driver installation
from typing import List, Dict, Optional  # Import type hints for better code clarity

# Define regex patterns for extracting emails and phone numbers
EMAIL_PATTERN = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}"  # Pattern to match email addresses
PHONE_PATTERN = r"(?:\+1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}(?:\s?(?:x|ext\.?)\s?\d+)?"  # Pattern to match US phone numbers

def scrape_url(url: str) -> str:
    """Fetch the webpage HTML source code using Selenium."""
    try:
        # Initialize Chrome WebDriver using WebDriver Manager
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        driver.get(url)  # Open the specified URL in the browser
        driver.implicitly_wait(5)  # Wait up to 5 seconds for elements to load
        html = driver.page_source  # Get the page source HTML

        driver.quit()  # Close the browser
        return html  # Return the HTML source code
    except Exception as e:
        print(f"Error fetching URL with Selenium: {e}")  # Print error message if any exception occurs
        return ""  # Return an empty string if fetching fails

def extract_contacts(html: str) -> List[Dict[str, Optional[str]]]:
    """Extract email addresses and phone numbers from HTML text."""
    text = html  # Store the HTML source as text
    print("Extracted text snippet (first 1000 chars):", text[:1000])  # Print first 1000 characters for debugging
    emails = set(re.findall(EMAIL_PATTERN, text))  # Find all email addresses using regex
    phones = set(re.findall(PHONE_PATTERN, text))  # Find all phone numbers using regex
    print("Emails found:", emails)  # Print found emails for debugging
    print("Phones found:", phones)  # Print found phones for debugging
    
    contacts = []  # Initialize an empty list to store contact details
    seen_entries = set()  # Create a set to track unique entries
    
    # Add email entries to the contact list
    for email in emails:
        entry = (email, None)  # Create a tuple with email and no phone
        if entry not in seen_entries:
            contacts.append({"email": email, "phone": None})  # Append to contacts list
            seen_entries.add(entry)  # Mark this entry as seen
    
    # Add phone entries to the contact list
    for phone in phones:
        entry = (None, phone)  # Create a tuple with phone and no email
        if entry not in seen_entries:
            if not emails or all(c["email"] for c in contacts):
                contacts.append({"email": None, "phone": phone})  # Add phone-only contact
            else:
                for contact in contacts:
                    if contact["phone"] is None and contact["email"]:
                        contact["phone"] = phone  # Pair phone with an existing email
                        break
            seen_entries.add(entry)  # Mark this entry as seen
    
    return contacts if contacts else [{"email": None, "phone": None}]  # Return extracted contacts

def save_to_csv(contacts: List[Dict[str, Optional[str]]], filename: str = "leads.csv"):
    """Save extracted contacts to a CSV file."""
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["email", "phone"])  # Define CSV column headers
        writer.writeheader()  # Write the header row
        writer.writerows(contacts)  # Write contact data rows
    print(f"\nResults saved: {len(contacts)} entries written to '{filename}'")  # Print confirmation message

def main():
    """Main function to parse arguments and run the scraper."""
    parser = argparse.ArgumentParser(description="Lead generation scraper for emails and phone numbers.")  # Set up argument parser
    parser.add_argument("--url", required=True, help="URL to scrape (e.g., https://example.com/contact)")  # Define URL argument
    args = parser.parse_args()  # Parse command-line arguments
    url = args.url  # Extract the URL from arguments
    
    print(f"\n=== Scraping {url} for emails and phone numbers ===")  # Print scraping start message
    html = scrape_url(url)  # Fetch webpage HTML
    if not html:
        print("Failed to retrieve content. Exiting.")  # Print failure message if no HTML is retrieved
        return
    
    contacts = extract_contacts(html)  # Extract contacts from HTML
    if not contacts:
        print("No data found.")  # Print message if no contacts are found
        return
    
    print("\n=== Extracted Data ===")  # Print extracted data section
    for i, contact in enumerate(contacts, 1):
        print(f"Entry {i}:")
        print(f"  Email:   {contact['email'] or 'Not Found'}")  # Print email (or 'Not Found')
        print(f"  Phone:   {contact['phone'] or 'Not Found'}")  # Print phone (or 'Not Found')
        print()
    
    save_to_csv(contacts)  # Save extracted contacts to CSV file

if __name__ == "__main__":
    main()  # Run the script if executed directly