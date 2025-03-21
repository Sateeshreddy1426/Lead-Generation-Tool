Lead Generation Scraper with ML-based Spam Detection

Overview

This project extracts emails and phone numbers from a given webpage and classifies emails as spam or valid using a Machine Learning (ML) model. The model is trained on extracted data or fallback training data.

Features

Web scraping using Selenium and BeautifulSoup

Email and phone number extraction using regex

Spam detection using Logistic Regression

Data storage in CSV format

Installation

Prerequisites

Ensure you have Python 3 installed. Install the required dependencies:

pip install -r requirements.txt

Dependencies

selenium

webdriver_manager

beautifulsoup4

pandas

scikit-learn

Usage

Scrape and classify contacts

python scraper.py --url "https://example.com/contact"

Train model with additional data

python scraper.py --url "https://example.com/contact" --training-url "https://example.com/training"

Output

Extracted contacts are saved in leads.csv with classification labels.

Report

Approach

The system scrapes emails and phone numbers from webpages and applies spam classification using a trained machine learning model. If an external training dataset is unavailable, fallback data is used.

Model Selection

We used Logistic Regression due to its efficiency in binary classification and ability to generalize well to unseen data.

Data Preprocessing

Emails are converted to lowercase

Domains are extracted as features for classification

Missing values are handled appropriately

Performance Evaluation

The model was trained using CountVectorizer + Logistic Regression and evaluated using a train-test split (80-20). Accuracy and precision-recall metrics were considered to assess performance.

Rationale

Logistic Regression provides a balance between interpretability and performance, making it a suitable choice for spam detection based on email domains.
