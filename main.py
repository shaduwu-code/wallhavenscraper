# A scraper for wallhaven.cc that downloads wallpapers
# ------------------------------------------------------------------------------
# ---------------------------------------------------- Import required modules
# Import requests module to make get request
from sys import exit
import re
import requests
# Import BeautifulSoup to parse the HTML
from bs4 import BeautifulSoup as bs
# Import os module to communicate with directories and getenv
import os
# import load_dotenv to load environment variables
from dotenv import load_dotenv
# Import argparse to parse command line arguments
import argparse
# Import alive_progress to show progress bar
from alive_progress import alive_bar
# Import time module to sleep for a while
import time
# ----------------------------------------------------
# Define the arguments
parser = argparse.ArgumentParser(
    description='Scrape wallpapers from wallhaven.cc')
# Search argument
parser.add_argument(
    '-s', '--search', help='Search term to search for', required=True, nargs='+')
# Purity argument
parser.add_argument('-p', '--purity', help='Purity of the wallpaper',
                    required=False, default='sfw', choices=['sfw', 'sketchy', 'nsfw'])
# Sort argument (default by date_added) (date_added, random, views, favorites, toplist)
parser.add_argument('-o', '--order', help='Order of the wallpapers', required=False,
                    default='date_added', choices=['date_added', 'random', 'views', 'favorites', 'toplist'])
# parse search argument with spaces
search = ' '.join(parser.parse_args().search)
# Assign the purity argument to purity
purity = parser.parse_args().purity
# Assign the order argument to order
order = parser.parse_args().order
# Import exit

# Iniate load_dotenv to load environment variables
load_dotenv()


class wallhaven:
    def __init__(self, search, purity, order):
        self.search = search
        self.purity = purity
        self.order = order
        apikey = os.getenv('WALLHAVEN_API_KEY')
        # Authantication Headers
        self.headers = {"X-API-Key": f"{apikey}"}
        # Search parameters
        self.params = {"sorting": order, "purity": purity}
    # Function to get the results

    def get_wallpapers(self, search):
        # Get the search results
        resbond = requests.get("https://wallhaven.cc/api/v1/search?q={}".format(
            search.replace(" ", "+")), headers=self.headers, params=self.params)
        # Format results in json
        results_json = resbond.json()
        # Get the data from the json
        results_data = results_json["data"]
        # Dictionary to store the results links
        results_links = {}
        for result in results_data:
            results_links[result["id"]] = result["path"]
        return results_links

    # Function to download the wallpapers
    def download_wallpapers(self, results_links, search):
        with alive_bar(len(results_links), stats=False, bar='bubbles', title=f'Wallhaven') as bar:
            for link in results_links:
                # Get current directory
                current_dir = os.getcwd()
                # Create directory for images
                image_dir = os.path.join(current_dir, "wallhaven_images")
                # Create directory for search query inside images
                search_dir = os.path.join(image_dir, search)
                # If the directory does not exist, create it
                if not os.path.exists(search_dir):
                    os.makedirs(search_dir)
                # Get the image link
                image_url = results_links[link]
                # Get the image name (id)
                image_name = image_url.split("/")[-1]
                # Change bar title
                bar.title = f'Wallhaven: Downlaoding {image_name}'
                # Set image path
                image_path = os.path.join(search_dir, image_name)
                # Cheack if the image already exists
                # If it does, skip it
                if os.path.exists(image_path):
                    #print(f'{image_name} already exists')
                    bar.title = f'Wallhaven: Skipping {image_name}, already exists'
                    time.sleep(0.3)
                    bar()
                    continue
                # If it does not, download it
                if not os.path.exists(image_path):
                    # Save the image
                    bar.title = f'Wallhaven: Downloading {image_name}'
                    with open(image_path, "wb") as f:
                        f.write(requests.get(image_url).content)
                    #print("Downloaded image: " + image_name)
                    time.sleep(0.3)
                    bar()


try:
    # Initiate the scraper
    wallhaven = wallhaven(search, purity, order)
    # Get the wallpapers
    wallpapers = wallhaven.get_wallpapers(search)
    # Download the wallpapers
    wallhaven.download_wallpapers(wallpapers, search)
except(KeyboardInterrupt):
    print("\nExiting...")
    exit()
except(Exception):
    print("\nError occured")
    exit()
