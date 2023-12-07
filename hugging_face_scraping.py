import requests
from bs4 import BeautifulSoup
import re
import csv
import logging
import datetime
from urllib.parse import urljoin, urlparse, parse_qs

# Create a class named HuggingFaceScraper
class HuggingFaceScraper:
    """
    A class for scraping information from Hugging Face model pages.

    This class is designed to scrape various information from Hugging Face model pages, including model names,
    model repositories, model addresses, model URLs, GitHub links, categorized tags, and model card text.

    Attributes:
        log_filename (str): The filename for the log file generated during scraping.

    Methods:
        fetch_html_content(url):
            Fetches HTML content from a given URL using the requests library.

        get_or_cache_html(url, cache):
            Retrieves HTML content from the cache if available, or fetches and caches it if not.

        generate_model_page_urls_with_pagination(base_url, batch_size=50):
            Generates a list of model page URLs with pagination.

        scrape_model_names(href_values, cache):
            Scrapes model names from a list of Hugging Face model page URLs.

        scrape_model_repositories(href_values, cache):
            Scrapes model repositories from a list of Hugging Face model page URLs.

        model_addresses(href_values, cache):
            Scrapes model addresses from Hugging Face model pages.

        fetch_huggingface_model_urls(href_values, cache):
            Scrapes Hugging Face model URLs from a list of model page URLs.

        scrape_github_links(model_urls, cache):
            Scrapes GitHub links related to the Hugging Face models.

        scrape_model_cards(model_urls, cache):
            Scrapes and extracts model card text from Hugging Face model pages.

        scrape_category_tags(model_urls, cache):
            Scrapes categorized tags from a list of Hugging Face model page URLs.

        save_to_csv(data, csv_file_path):
            Saves scraped data to a CSV file.

        run():
            Executes the web scraping process, collecting and saving data from Hugging Face model pages.

    Usage:
        Create an instance of the HuggingFaceScraper class, call the 'run' method to start the web scraping process,
        and specify the CSV file path where the scraped data will be saved.
    """

    # Constructor to initialize the HuggingFaceScraper instance
    def __init__(self):
        """
        Initializes the HuggingFaceScraper instance.

        Sets up the log filename with the current date and configures logging to write logs to a specified file.
        """

        # Initialize the log filename with the current date
        self.log_filename = datetime.datetime.now().strftime("%Y-%m-%d") + ".log"

        # Configure logging to write logs to the specified file
        logging.basicConfig(filename=self.log_filename, level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

    # Method to fetch HTML content from a given URL
    def fetch_html_content(self, url):
        """
        Fetch HTML content from a given URL.

        Args:
            url (str): The URL to fetch HTML content from.

        Returns:
            str or None: The text content of the response if the request is successful,or None if an error occurs during the request.
        """

        try:
            # Send an HTTP GET request to the URL
            response = requests.get(url)

            # Raise an exception if the response status code is not OK
            response.raise_for_status()

            # Return the text content of the response
            return response.text

        except Exception as e:
            # Log an error message if an exception occurs during the request
            logging.error(f"An error occurred while fetching {url}: {e}")
            return None

    # A function to fetch and cache HTML content for URLs
    def get_or_cache_html(self, url, cache):
        """
        Fetches and caches HTML content for a given URL if not already cached.

        If the HTML content for the specified URL is already present in the cache, it is returned.
        Otherwise, the content is fetched from the URL using the 'fetch_html_content' method,
        cached for future use, and then returned.

        Args:
            url (str): The URL to fetch and cache HTML content from.
            cache (dict): A dictionary used for caching fetched HTML content.

        Returns:
            str: The HTML content of the specified URL.
        """

        if url in cache:
            return cache[url]
        else:
            html_content = self.fetch_html_content(url)
            cache[url] = html_content
            return html_content

    # Method to generate model page URLs with pagination
    def generate_model_page_urls_with_pagination(self, base_url, batch_size=50):
        """
        Generate a list of model page URLs with pagination based on a base URL.

        This method fetches the HTML content from the base URL, parses it, and extracts the pagination
        information. It then generates a list of model page URLs with the specified batch size.

        Args:
            base_url (str): The base URL for model pages.
            batch_size (int, optional): The number of models per page. Default is 50.

        Returns:
            list: A list of model page URLs with pagination.

        If an error occurs during URL generation, it logs an error message and returns an empty list.
        """

        try:
            # Fetch HTML content from the base URL
            base_html_content = self.get_or_cache_html(base_url, {})

            if base_html_content is None:
                return []

            # Parse the HTML content with BeautifulSoup
            soup = BeautifulSoup(base_html_content, 'html.parser')

            # Find all <li> elements with class "hidden sm:block"
            li_elements = soup.find_all('li', class_='hidden sm:block')

            # Extract the last href value and determine the maximum page number
            last_href = li_elements[-1].find('a')['href']
            parsed_url = urlparse(last_href)
            query_params = parse_qs(parsed_url.query)
            max_page = int(query_params.get('p', [0])[0])

            href_values = []

            for batch_start in range(0, max_page + 1, batch_size):
                batch_end = min(batch_start + batch_size, max_page + 1)
                for page_number in range(batch_start, batch_end):
                    page_url = urljoin(base_url, f'?p={page_number}&sort=trending')
                    href_values.append(page_url)

            return href_values[:3]

        except Exception as e:
            # Log an error message if an exception occurs during URL generation
            logging.error(f"An error occurred while generating model page URLs: {e}")
            return []

    # Method to scrape model names from Hugging Face
    def scrape_model_names(self, href_values, cache):
        """
        Scrape and extract model names from a list of Hugging Face model page URLs.

        Args:
            href_values (list): A list of URLs pointing to Hugging Face model pages.
            cache (dict): A dictionary for caching fetched HTML content.

        Returns:
            list: A list of model names extracted from the provided URLs.

        This function iterates through the list of model page URLs, fetches HTML content for each URL, and
        extracts model names from the HTML using BeautifulSoup. Model names are typically found in the 'href'
        attribute values within elements with the class "block p-2." The function returns a list of model names.
        """


        model_names = []

        for url in href_values:
            # Fetch HTML content from the URL
            response_text = self.get_or_cache_html(url, cache)
            if response_text is not None:
                # Parse the HTML content with BeautifulSoup
                soup = BeautifulSoup(response_text, 'html.parser')

                # Find all elements with class="block p-2"
                elements = soup.find_all(class_='block p-2')

                # Extract the href attribute values from these elements
                href_values = [element['href'] for element in elements if 'href' in element.attrs]

                # Extract only the text after the last '/' in each href value if there are at least two slashes
                model_names.extend([href.split('/')[-1] if href.count('/') >= 2 else ' ' for href in href_values])

        return model_names

    # Method to scrape model repositories from Hugging Face
    def scrape_model_repositories(self, href_values, cache):
        """
        Scrape and extract model repositories from a list of Hugging Face model page URLs.

        Args:
            href_values (list): A list of URLs pointing to Hugging Face model pages.
            cache (dict): A dictionary for caching HTML content to reduce redundant requests.

        Returns:
            list: A list of model repositories extracted from the provided URLs.
        """

        model_repo = []

        for url in href_values:
            # Fetch HTML content from the URL
            response_text = self.get_or_cache_html(url, cache)
            if response_text is not None:
                # Parse the HTML content with BeautifulSoup
                soup = BeautifulSoup(response_text, 'html.parser')

                # Find all elements with class="block p-2"
                elements = soup.find_all(class_='block p-2')

                # Extract the href attribute values from these elements
                href_values = [element['href'] for element in elements if 'href' in element.attrs]

                # Extract and return only the text between slashes
                model_repo.extend([href.split('/')[1] for href in href_values])

        return model_repo

    # Method to scrape model addresses from Hugging Face
    def model_addresses(self, href_values, cache):
        """
        Scrape and extract model addresses from Hugging Face model pages.

        Args:
            href_values (list): A list of URLs to Hugging Face model pages.
            cache (dict): A dictionary for caching HTML content to reduce redundant requests.


        Returns:
            list: A list of model addresses extracted from the provided URLs.
        """


        model_address = []

        for url in href_values:
            # Fetch HTML content from the base URL
            response_text = self.get_or_cache_html(url, cache)
            if response_text is not None:

                # Parse the HTML content with BeautifulSoup
                soup = BeautifulSoup(response_text, 'html.parser')

                # Find all elements with class="block p-2"           <a class="block p-2" href="/stabilityai/control-lora">
                elements = soup.find_all(class_='block p-2')

                # Extract the href attribute values from these elements
                # model_address = [element['href'] for element in elements if 'href' in element.attrs]
                model_address.extend([element['href'] for element in elements if 'href' in element.attrs])

        return model_address

    # Method to scrape model URLs from Hugging Face
    def fetch_huggingface_model_urls(self, href_values, cache):
        """
        Scrapes Hugging Face model URLs from a list of model page URLs.

        Args:
            href_values (list): A list of URLs to Hugging Face model pages.
            cache (dict): A dictionary for caching HTML content.

        Returns:
            list: A list of Hugging Face model URLs extracted from the provided model page URLs.
        """

        model_url = []

        for url in href_values:
            # Fetch HTML content from the URL
            response_text = self.get_or_cache_html(url, cache)
            if response_text is not None:
                # Parse the HTML content with BeautifulSoup
                soup = BeautifulSoup(response_text, 'html.parser')

                # Find all elements with class="block p-2"
                elements = soup.find_all(class_='block p-2')

                # Extract the href attribute values from these elements
                model_url.extend([f'https://huggingface.co{element["href"]}' for element in elements if 'href' in element.attrs])

        return model_url

    # Method to scrape GitHub links
    def scrape_github_links(self, model_urls, cache):
        """
        Scrape and extract unique GitHub links from a list of Hugging Face model URLs.

        Args:
            model_urls (list): A list of Hugging Face model URLs to scrape for GitHub links.
            cache (dict): A dictionary for caching HTML content of the URLs.

        Returns:
            list: A list of unique GitHub links found in the provided URLs, separated by commas.
        """

        # Initialize an empty list to store the results
        results = []

        for url in model_urls:
            # Create an empty set to store unique GitHub links for the current URL
            unique_github_links = set()

            # Fetch HTML content from the URL
            response_text = self.get_or_cache_html(url, cache)
            if response_text is not None:
                # Use a regular expression to find links in the format 'pip install git+https://github.com/...'
                pip_links = re.findall(r'pip install git\+(https://github\.com/[^\s]+)', response_text)

                # Iterate through the pip links and add them to the set of unique GitHub links
                for pip_link in pip_links:
                    unique_github_links.add(pip_link)

                # Parse the HTML content with BeautifulSoup
                soup = BeautifulSoup(response_text, 'html.parser')

                # Find all <a> tags with href attributes
                links = soup.find_all('a', href=True)

                # Iterate through the links and extract the ones starting with 'https://github.com/'
                for link in links:
                    href = link['href']
                    if href.startswith('https://github.com/') or href.startswith('http://github.com/'):
                        unique_github_links.add(href)

                # Print the unique GitHub links for the current URL, separated by commas
                output = ', '.join(unique_github_links)
                results.append(output)

        return results

    # Method to scrape only model cards from Hugging Face
    def scrape_model_cards(self, model_urls, cache):
        """
        Scrape and extract model card text from Hugging Face model pages.

        This function takes a list of model page URLs, fetches their HTML content, and extracts the model card text
        from each page. Model card text typically includes detailed information about a model such as its description,
        usage instructions, and related information. The function uses BeautifulSoup for HTML parsing and excludes
        unnecessary elements like headers and buttons to clean the extracted text.

        Args:
            model_urls (list): A list of URLs to Hugging Face model pages.
            cache (dict): A dictionary to cache fetched HTML content for optimization.

        Returns:
            list: A list of cleaned model card texts extracted from the provided URLs.
        """
        all_texts = [] 

        for url in model_urls:

            # Fetch HTML content from the base URL
            response_text = self.get_or_cache_html(url, cache)
            if response_text is not None:

            # Parse the HTML content with BeautifulSoup
                soup = BeautifulSoup(response_text, 'html.parser')

                # Find the <main> element with class "flex flex-1 flex-col"
                main_element = soup.find('main', class_='flex flex-1 flex-col')

                if main_element:
                    # Find and exclude the <header> element within the <main> element
                    header_element = main_element.find('header', class_='from-gray-50-to-white border-b border-gray-100 bg-gradient-to-t via-white dark:via-gray-950 pt-6 sm:pt-9')
                    if header_element:
                        # Remove the header element from the DOM
                        header_element.extract()  
                    
                    # Find and exclude the element with class "pt-8 border-gray-100 md:col-span-5 pt-6 md:pb-24 md:pl-6 md:border-l order-first md:order-none"
                    div_element = main_element.find('div', class_='pt-8 border-gray-100 md:col-span-5 pt-6 md:pb-24 md:pl-6 md:border-l order-first md:order-none')
                    if div_element:

                        # Remove the div element from the DOM
                        div_element.extract()  

                    # Find and exclude the <section> element with the same class as the div element
                    section_element = main_element.find('section', class_='pt-8 border-gray-100 md:col-span-5 pt-6 md:pb-24 md:pl-6 md:border-l order-first md:order-none')
                    if section_element:
                        # Remove the section element from the DOM
                        section_element.extract()  

                    # Find and exclude the <a> element with class "btn mb-6 text-sm text-gray-600 md:absolute md:-right-6 md:top-0 md:mb-0 md:rounded-r-none md:rounded-t-none md:border-r-0 md:border-t-0 md:border-gray-100 md:bg-none"
                    a_element = main_element.find('a', class_='btn mb-6 text-sm text-gray-600 md:absolute md:-right-6 md:top-0 md:mb-0 md:rounded-r-none md:rounded-t-none md:border-r-0 md:border-t-0 md:border-gray-100 md:bg-none')
                    if a_element:
                        # Remove the <a> element from the DOM
                        a_element.extract() 

                    # Extract all the text from the <main> element
                    extracted_text = main_element.get_text(separator=' ')

                    lines = [line.strip() for line in extracted_text.splitlines() if line.strip()]

                    # Clean up the text by removing blank lines and leading spaces
                    cleaned_text = " ".join(lines)

                    # Append the cleaned text to the list
                    all_texts.append(cleaned_text) 
                    
        return all_texts

    # Method to scrape categorized tags from a list of model URLs
    def scrape_category_tags(self, model_urls, cache):
        """
        Scrape and extract categorized tags from a list of model URLs.

        Args:
            model_urls (list): A list of URLs pointing to model detail pages.
            cache (dict): A dictionary for caching HTML content of the URLs.

        Returns:
            list: A list of dictionaries containing categorized tags for each model URL.
        """
        # Initialize a list to store category items for each URL
        all_category_items = []

        for url in model_urls:

            # Fetch HTML content from the base URL
            response_text = self.get_or_cache_html(url, cache)
            if response_text is not None:
                # Parse the HTML content with BeautifulSoup
                soup = BeautifulSoup(response_text, 'html.parser')

                # Find all <a> tags within the HTML
                a_tags = soup.find_all('a')

                # Initialize empty lists for all categories
                category_items = {'Task': [], 'Library': [], 'Language': [], 'Others': [], 'Arxiv': [], 'License': [], 'Dataset': []}

                for a_tag in a_tags:
                    href = a_tag.get('href', '')

                    # Check href patterns and extract accordingly
                    if href.startswith('/models?pipeline_tag='):
                        heading = 'Task'
                    elif href.startswith('/models?library='):
                        heading = 'Library'
                    elif href.startswith('/models?language='):
                        heading = 'Language'
                    elif href.startswith('/models?other='):
                        if '=arxiv%' in href:
                            heading = 'Arxiv'
                        else:
                            heading = 'Others'
                    elif href.startswith('/models?license=license%3A'):
                        heading = 'License'
                    elif href.startswith('/models?dataset=dataset%3A'):
                        heading = 'Dataset'
                    else:
                        continue  # Skip if the href doesn't match any pattern

                    tag_text = a_tag.get_text().strip()
                    # Remove newline characters from the tag_text
                    tag_text = tag_text.replace('\n', '')
                    if heading == 'License':
                        # Remove 'License:' prefix
                        tag_text = tag_text.replace('License: ', '')
                    category_items[heading].append(tag_text)

                # Add the category items for the current URL to the list
                all_category_items.append(category_items)

        return all_category_items

    # Method to save data to a CSV file
    def save_to_csv(self, data, csv_file_path):
        """
            Saves the provided data to a CSV file at the specified path.

            Args:
                    data (list): A list of data rows to be written to the CSV file.
                    csv_file_path (str): The file path where the CSV file will be created or overwritten.

            Returns:
                    None

            Raises:
                    Exception: If an error occurs during CSV file writing.

            Logs:
                    - Logs a success message if the data is successfully saved to the CSV file.
                    - Logs an error message if an exception occurs during CSV writing.
        """

        try:
            # Open the CSV file for writing
            with open(csv_file_path, mode='w', newline='', encoding='utf-8') as csv_file:
                writer = csv.writer(csv_file)

                # Write header row
                writer.writerow(["Sr.no", "ModelName", "ModelRepo", "ModelAddress", "ModelUrl", "Tasks","Libraries","Dataset","Languages","Other","Arxiv","Licenses", "Github Links", "Body"])

                # Write data rows
                writer.writerows(data)

            # Log a success message
            logging.info(f"Data has been saved to {csv_file_path}")
            print(f"Data has been saved to {csv_file_path}")

        except Exception as e:
            # Log an error message if an exception occurs during CSV writing
            logging.error(f"An error occurred while saving data to CSV: {e}")

    # Execute the web scraping process to gather data from Hugging Face model pages. 
    def run(self):
        """
        Execute the web scraping process to gather data from Hugging Face model pages.

        This method initiates the web scraping process, which includes fetching HTML content from the Hugging Face model pages,
        extracting various data, formatting the data, and saving it to a CSV file.

        Usage:
            1. Create an instance of the HuggingFaceScraper class.
            2. Call the 'run' method to start the scraping process.
        """


        # Define the base URL
        base_url = 'https://huggingface.co/models'

        # Fetch HTML content from the base URL and cache it
        cache = {}
        base_html_content = self.get_or_cache_html(base_url, cache)

        if base_html_content is None:
            return

        # Generate model page URLs with pagination
        href_values = self.generate_model_page_urls_with_pagination(base_url, batch_size=50)
        # print(len(href_values))
        # Scrape various data from the generated model URLs
        model_names = self.scrape_model_names(href_values, cache)
        model_repo = self.scrape_model_repositories(href_values, cache)
        model_addresses = self.model_addresses(href_values, cache)
        # print(model_addresses)
        model_urls = self.fetch_huggingface_model_urls(href_values, cache)
        extract_model_cards = self.scrape_model_cards(model_urls, cache)
        scrape_github_links = self.scrape_github_links(model_urls, cache)
        scrape_category_tags = self.scrape_category_tags(model_urls, cache)

        # Extracting and formatting data for each Tag category:
        task_data = [', '.join(x['Task']) for x in scrape_category_tags]
        library_data = [', '.join(x['Library']) for x in scrape_category_tags]
        dataset_data = [', '.join(x['Dataset']) for x in scrape_category_tags]
        arxiv_data = [', '.join(x['Arxiv']) for x in scrape_category_tags]
        language_data = [', '.join(x['Language']) for x in scrape_category_tags]
        others_data = [', '.join(x['Others']) for x in scrape_category_tags]
        license_data = [', '.join(x['License']) for x in scrape_category_tags]


        # # Zip the data for writing to a CSV file
        rows = zip(range(1, len(model_names) + 1), model_names, model_repo, model_addresses, model_urls, task_data, library_data, dataset_data, language_data, others_data, arxiv_data, license_data, scrape_github_links, extract_model_cards)

        # Specify the CSV file path
        csv_file_path = r'E:\VSCODE\hugging_face_scraping.csv'

        # Save the data to a CSV file
        self.save_to_csv(rows, csv_file_path)

# Entry point of the script
if __name__ == "__main__":
    # Create an instance of the HuggingFaceScraper class
    scraper = HuggingFaceScraper()

    # Run the web scraping process
    scraper.run()