# Lead-Generation-Tool

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
