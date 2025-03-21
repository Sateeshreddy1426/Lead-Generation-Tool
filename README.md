# Lead-Generation-Tool

Lead Generation Scraper with ML-Based Spam Detection

1. Introduction

This project extracts email addresses and phone numbers from web pages and classifies emails as spam or valid using a machine learning model. The goal is to automate lead generation while filtering out spam contacts.

2. Approach

Web Scraping: Selenium fetches the webpage content.

Regex Matching: Extracts emails and phone numbers using predefined regex patterns.

Machine Learning Model:

Feature: Extracted email domain.

Model: Logistic Regression trained on labeled email domains.

Preprocessing: Used CountVectorizer to convert email domains into numerical features.

3. Model Selection & Rationale

Why Logistic Regression?

Simple, efficient, and interpretable for binary classification (Spam vs. Valid).

Works well with small datasets.

Alternatives Considered:

Random Forest (higher accuracy but less interpretable).

Deep Learning (overkill for small datasets).

4. Performance Evaluation

Accuracy: ~80% on a small dataset.

Limitations:

Relies only on email domains; does not analyze content.

Small training dataset may lead to biased results.

5. Future Improvements

Collect a larger dataset for better spam detection.

Use NLP techniques for email content analysis.

Implement an API for real-time classification.

Expand features (e.g., frequency of email domain occurrences, blacklist matching).

# Lead Generation Scraper

A tool to scrape company details (name, address) and contacts (emails, phone numbers) from a URL, outputting results in CSV format. Built for the Caprae Capital AI-Readiness Pre-Screening Challenge.

## Setup Instructions

1. **Install Dependencies**:
   ```bash
   pip install requests beautifulsoup4
   pip install selenium
   pip install webdriver-manager


To run the script
python lead_scraper.py --url <target_url>

# you can do this in another way
# Install dependencies
!pip install requests beautifulsoup4

# Run the scraper
!python lead_scraper.py --url https://getcohesiveai.com/scraper


