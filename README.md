# Lead-Generation-Tool

Lead Generation Scraper

Overview

This project is a web scraping tool designed to extract business leads from websites. It collects company details such as names, emails, phone numbers, and addresses from a given URL. The extracted data can be used for lead generation and business outreach.

Features

Scrapes company details from a given webpage

Extracts emails, phone numbers, and addresses using regex

Filters and removes duplicate entries

Saves extracted data into structured formats

Can be extended for CRM integration or automation

# Lead Generation Scraper

A tool to scrape company details (name, address) and contacts (emails, phone numbers) from a URL, outputting results in CSV format. Built for the Caprae Capital AI-Readiness Pre-Screening Challenge.

## Setup Instructions

1. **Install Dependencies**:
   ```bash
   pip install requests beautifulsoup4

To run the script
python lead_scraper.py --url <target_url>

# you can do this in another way
# Install dependencies
!pip install requests beautifulsoup4

# Run the scraper
!python lead_scraper.py --url https://getcohesiveai.com/scraper

# Display output
import pandas as pd
df = pd.read_csv("leads.csv")
df
