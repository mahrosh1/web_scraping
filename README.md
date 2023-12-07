# Hugging Face Model Scraper
The Hugging Face Model Scraper is a Python web scraping tool designed to extract valuable information from Hugging Face model pages. It automates the process of gathering data such as model names, repositories, addresses, URLs, GitHub links, categorized tags, and model card text. The scraped data is then formatted and saved into a CSV file for easy analysis.

## Table of Contents
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Documentation](#documentation)

## Features
- **Scrape Multiple Data Points:** Extracts model names, repositories, addresses, URLs, GitHub links, categorized tags, and model card text from Hugging Face model pages.
- **Categorized Tags:** Tags are categorized into tasks, libraries, datasets, languages, and more, providing a structured overview of each model.
- **GitHub Link Extraction:** Automatically extracts GitHub links related to the Hugging Face models.
- **CSV Output:** Saves the scraped data into a CSV file for easy data analysis and manipulation.
- **Logging:** Logs errors and information during the scraping process for easy debugging.

## Requirements
- Python 3
- Libraries: requests, BeautifulSoup (bs4)

## Installation
1. Clone the repository to your local machine:
          ```bash
           git clone https://github.com/mahrosh1/web_scraping.git
           cd web_scraping
2. Install the required Python libraries:
           pip install -r requirements.txt

## Usage
1. Open a terminal and navigate to the project directory.
2. Run the script:
          python hugging_face_scraping.py
3. The scraped data will be saved to a CSV file (hugging_face_scraping.csv by default) in the project directory.

## Documentation
Class: HuggingFaceScraper
## Methods:
- **run():** Initiates the web scraping process.
- **fetch_html_content(url):** Fetches HTML content from a given URL.
- **get_or_cache_html(url, cache):** Retrieves HTML content from the cache or fetches and caches it.
- **generate_model_page_urls_with_pagination(base_url, batch_size=50):** Generates a list of model page URLs with pagination.
- **scrape_model_names(href_values, cache):** Scrapes model names from a list of Hugging Face model page URLs.
- **scrape_model_repositories(href_values, cache):** Scrapes model repositories from a list of Hugging Face model page URLs.
- **model_addresses(href_values, cache):** Scrapes model addresses from Hugging Face model pages.
- **fetch_huggingface_model_urls(href_values, cache):** Scrapes Hugging Face model URLs from a list of model page URLs.
- **scrape_github_links(model_urls, cache):** Scrapes GitHub links related to the Hugging Face models.
- **scrape_model_cards(model_urls, cache):** Scrapes and extracts model card text from Hugging Face model pages.
- **scrape_category_tags(model_urls, cache):** Scrapes categorized tags from a list of Hugging Face model page URLs.
- **save_to_csv(data, csv_file_path):** Saves scraped data to a CSV file.
