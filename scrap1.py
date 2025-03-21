import re  # Regular expressions for pattern matching
import csv  # CSV file handling
import argparse  # Command-line argument parsing
import pandas as pd  # Data handling and manipulation
from selenium import webdriver  # Web scraping using Selenium
from selenium.webdriver.chrome.service import Service  # Chrome service manager
from webdriver_manager.chrome import ChromeDriverManager  # Auto-install ChromeDriver
from bs4 import BeautifulSoup  # Parsing HTML content
from typing import List, Dict, Optional  # Type hinting
from sklearn.feature_extraction.text import CountVectorizer  # Feature extraction for ML
from sklearn.model_selection import train_test_split  # Splitting dataset for ML training
from sklearn.linear_model import LogisticRegression  # ML model for classification
from sklearn.pipeline import make_pipeline  # Creating a pipeline for ML model

# Regex patterns
EMAIL_PATTERN = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}"
PHONE_PATTERN = r"(?:\+1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}(?:\s?(?:x|ext\.?)\s?\d+)?"

# ML Model Placeholder
model = None

def scrape_url(url: str) -> str:
    """Scrape the given URL and return its HTML content."""
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        driver.get(url)
        driver.implicitly_wait(5)
        html = driver.page_source
        driver.quit()
        return html
    except Exception as e:
        print(f"Error fetching URL: {e}")
        return ""

def extract_training_data(html: str) -> List[Dict[str, Optional[str]]]:
    """Extract training data (email, phone, label) from HTML."""
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(separator=" ")
    
    training_pattern = r"(spam|valid):\s*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}),\s*(\+?1?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})"
    matches = re.findall(training_pattern, text, re.IGNORECASE)
    
    training_data = []
    for match in matches:
        label_str, email, phone = match
        label = 1 if label_str.lower() == "spam" else 0
        training_data.append({"email": email.lower().strip(), "phone": re.sub(r"\D", "", phone), "label": label})
    
    if not training_data:
        print("No training data found on page. Using fallback data.")
        training_data = [
        {"email": "spam123@gmail.com", "label": 1},  # Spam
        {"email": "business@company.com", "label": 0},  # Valid
        {"email": "fakelead@random.net", "label": 1},  # Spam
        {"email": "client@xyzcorp.com", "label": 0},  # Valid
        {"email": "junkmail@yahoo.com", "label": 1},  # Spam
        {"email": "support@nonprofit.org", "label": 0},  # Valid
        {"email": "spammer99@hotmail.com", "label": 1},  # Spam
        {"email": "info@techfirm.co", "label": 0},  # Valid
        {"email": "random345@freemail.com", "label": 1},  # Spam
        {"email": "hr@startup.io", "label": 0},  # Valid
        {"email": "testspam@outlook.com", "label": 1},  # Spam
        {"email": "contact@university.edu", "label": 0}  # Valid
    ]
    
    return training_data

def train_model(training_html: str):
    """Train an ML model for spam classification using data from a website."""
    global model
    data = extract_training_data(training_html)
    
    df = pd.DataFrame(data)
    df["email_domain"] = df["email"].apply(lambda x: x.split("@")[-1] if pd.notna(x) else "unknown")
    
    X = df["email_domain"]
    y = df["label"]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = make_pipeline(CountVectorizer(), LogisticRegression())
    model.fit(X_train, y_train)
    print("Model trained successfully with", len(data), "entries!")

def classify_contact(email: str) -> str:
    """Classify a contact as 'spam' or 'valid' based on email domain."""
    if not email or not model:
        return "Unknown"
    email_domain = email.split("@")[-1]
    prediction = model.predict([email_domain])[0]
    return "Spam" if prediction == 1 else "Valid"

def extract_contacts(html: str) -> List[Dict[str, Optional[str]]]:
    """Extract email addresses and phone numbers from the HTML content."""
    emails = set(re.findall(EMAIL_PATTERN, html))
    phones = set(re.findall(PHONE_PATTERN, html))

    contacts = []
    seen_entries = set()

    for email in emails:
        email = email.lower().strip()
        entry = (email, None)
        if entry not in seen_entries:
            contacts.append({"email": email, "phone": None})
            seen_entries.add(entry)

    for phone in phones:
        phone = re.sub(r"\D", "", phone)
        entry = (None, phone)
        if entry not in seen_entries:
            if not emails or all(c["email"] for c in contacts):
                contacts.append({"email": None, "phone": phone})
            else:
                for contact in contacts:
                    if contact["phone"] is None and contact["email"]:
                        contact["phone"] = phone
                        break
            seen_entries.add(entry)

    return contacts if contacts else [{"email": None, "phone": None}]

def save_to_csv(contacts: List[Dict[str, Optional[str]]], filename: str = "leads.csv"):
    """Save the extracted contacts to a CSV file."""
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["email", "phone", "classification"])
        writer.writeheader()
        for contact in contacts:
            classification = classify_contact(contact["email"]) if contact["email"] else "Unknown"
            contact["classification"] = classification
            writer.writerow(contact)
    
    print(f"\nResults saved: {len(contacts)} entries written to '{filename}'")

def main():
    """Main function to handle argument parsing and execution."""
    parser = argparse.ArgumentParser(description="Lead generation scraper with ML-based spam detection.")
    parser.add_argument("--url", required=True, help="URL to scrape for contacts (e.g., https://example.com/contact)")
    parser.add_argument("--training-url", help="URL to scrape for training data (optional)")
    args = parser.parse_args()

    print("\n=== Training ML Model ===")
    if args.training_url:
        training_html = scrape_url(args.training_url)
        if training_html:
            train_model(training_html)
        else:
            print("Failed to fetch training URL. Using fallback data.")
            train_model("")
    else:
        print("No training URL provided. Using fallback data.")
        train_model("")

    print(f"\n=== Scraping {args.url} for emails and phone numbers ===")
    html = scrape_url(args.url)
    if not html:
        print("Failed to retrieve content. Exiting.")
        return

    contacts = extract_contacts(html)
    if not contacts:
        print("No data found.")
        return

    print("\n=== Extracted Data ===")
    for i, contact in enumerate(contacts, 1):
        classification = classify_contact(contact["email"]) if contact["email"] else "Unknown"
        print(f"Entry {i}:")
        print(f"  Email:   {contact['email'] or 'Not Found'}")
        print(f"  Phone:   {contact['phone'] or 'Not Found'}")
        print(f"  Class:   {classification}")
        print()

    save_to_csv(contacts)

if __name__ == "__main__":
    main()