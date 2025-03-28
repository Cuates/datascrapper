"""
This script defines a web scraper to fetch data from an API and save it to a JSON file.

The script uses the following:
- Requests library to handle HTTP requests.
- JSON library to handle JSON data.
- Datetime library to handle date and time for logging and file naming.
- Pathlib library to handle file path operations.
- ANSI escape sequences for colored terminal output.

The script defines a WebScraper class which:
- Initializes with a configuration dictionary containing API details.
- Fetches content from the API.
- Scrapes data for specified categories.
- Saves the scraped data to a JSON file.
- Logs the execution time of the script.

Usage:
    Modify the CONFIG constants in the main block to match your environment, then run the script.

    python dta_scrapper_tpdb.py

Dependencies:
    - requests

Pip:
    Make sure your pip is updated
    python.exe -m pip install --upgrade pip

Windows:
    If warning on a Windows machine perform the following
    WARNING: The scripts pip.exe, pip3.12.exe and pip3.exe are installed in 'C:\\Users\\<user_name>\\AppData\\Roaming\\Python\\Python312\\Scripts' which is not on PATH.
    Consider adding this directory to PATH or, if you prefer to suppress this warning, use --no-warn-script-location.

Installation:
Ensure you have Docker installed and running on your machine.
Install the required Python package:
    pip install requests
"""

import json
from datetime import datetime
from pathlib import Path
import requests
from typing import Dict, List, Optional, Union

def rgb_color(r: int, g: int, b: int, text: str) -> str:
    """
    Returns a string with ANSI escape codes for colored terminal output.

    Args:
        r (int): Red component of the color (0-255).
        g (int): Green component of the color (0-255).
        b (int): Blue component of the color (0-255).
        text (str): The text to be colored.

    Returns:
        str: The text wrapped in ANSI escape codes for the specified color.
    """
    return f"\033[38;2;{r};{g};{b}m{text}\033[0m"

class WebScraper:
    """
    A web scraper to fetch and save data from a specified API.

    Attributes:
        config (Dict[str, Union[str, List[str]]]): Configuration dictionary containing base_url, api_url, api_key, and categories.
        base_url (str): Base URL for the API.
        api_url (str): Full API URL.
        url_and_base (str): Concatenated API and base URL.
        api_key (str): API key for authentication.
        categories (List[str]): List of categories to scrape.
        session (requests.Session): HTTP session for making requests.
        all_data (Dict[str, List[Dict]]): Dictionary to store scraped data.
    """

    def __init__(self, config: Dict[str, Union[str, List[str]]]):
        """
        Initializes the WebScraper with a configuration dictionary.

        Args:
            config (Dict[str, Union[str, List[str]]]): Configuration dictionary containing base_url, api_url, api_key, and categories.
        """
        self.config = config
        self.base_url: str = self.config['base_url']
        self.api_url: str = self.config['api_url']
        self.url_and_base: str = self.api_url + self.base_url
        self.api_key: str = self.config['api_key']
        self.categories: List[str] = self.config['categories']
        self.session: requests.Session = requests.Session()
        self.session.headers.update({'Authorization': f'Bearer {self.api_key}'})
        self.all_data: Dict[str, List[Dict]] = {}

    def fetch_content(self, url: str) -> Optional[Dict]:
        """
        Fetches content from a given URL and returns the JSON response.

        Args:
            url (str): URL to fetch content from.

        Returns:
            Optional[Dict]: JSON response if the request is successful, None otherwise.
        """
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(rgb_color(255, 0, 0, f"Error fetching content for {url}: {e}"))
            return None

    def scrape_category(self, category: str) -> None:
        """
        Scrapes data for a given category.

        Args:
            category (str): Category to scrape data for.
        """
        category_url = f'{self.url_and_base}?letter={category}'
        while category_url:
            json_data = self.fetch_content(category_url)
            if (json_data):
                target_data = json_data.get('data')
                if (target_data):
                    self.all_data.setdefault(category, []).extend(target_data)
                    next_page_url = json_data.get('links', {}).get('next')
                    string_split = next_page_url.split('?', 1)[1] if next_page_url else None
                    category_url = f"{self.url_and_base}?letter={category}&{string_split}" if next_page_url else None
                else:
                    print(rgb_color(255, 255, 0, f"JSON Data not found for category {category}."))
                    category_url = None
            else:
                category_url = None

    def run_scraper(self) -> None:
        """
        Executes the scraper for all categories and saves the data.
        """
        print(rgb_color(0, 255, 0, f"Executing script with {self.api_url}"))
        for category in self.categories:
            print(rgb_color(255, 255, 0, f"{category}"))
            self.scrape_category(category)
        self.save_data()

    def save_data(self) -> None:
        """
        Saves the scraped data to a JSON file.
        """
        if self.all_data:
            now = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            script_dir = Path(__file__).parent
            output_file = script_dir / f'output_{now}.json'

            with output_file.open('w', encoding='utf-8') as json_file:
                json.dump(self.all_data, json_file, indent=2)
            print(rgb_color(0, 255, 0, f"Data successfully saved to {output_file}"))
        else:
            print(rgb_color(255, 255, 0, f"No data returned in the array {self.all_data}"))

if __name__ == "__main__":
    CONFIG: Dict[str, Union[str, List[str]]] = {
        'base_url': '<base_url>',
        'api_url': '<api_url>',
        'api_key': 'api_key',
        'categories': ['0-9', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
    }

    # Get the start time
    start_time = datetime.now()
    print(rgb_color(0, 255, 255, f"Script started at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}"))

    scraper = WebScraper(CONFIG)
    scraper.run_scraper()

    # Get the end time
    end_time = datetime.now()
    print(rgb_color(0, 255, 255, f"Script finished at: {end_time.strftime('%Y-%m-%d %H:%M:%S')}"))

    # Calculate and print the execution time
    execution_time = end_time - start_time
    print(rgb_color(201, 103, 28, f"Total execution time: {str(execution_time)}"))
