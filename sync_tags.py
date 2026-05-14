import cloudscraper
from bs4 import BeautifulSoup
import json
import re
import os

# Tag Set URL
URLS = {
    "all": "https://archiveofourown.org/tag_sets/28436",
    "round_specific": "https://archiveofourown.org/tag_sets/29146"
}

file_path = 'search/tags.json'

def scrape_url(scraper, url):
    try:
        response = scraper.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        extracted_tags = []

        freeform_lists = soup.find_all('ol', id=re.compile(r'list_for_freeform'))

        if freeform_lists:
            for lst in freeform_lists:
                tags = [li.get_text(strip=True) for li in lst.find_all('li')]
                extracted_tags.extend(tags)
            
            unique_tags = list(dict.fromkeys(extracted_tags))
            print(f"Successfully scraped {url}. Found {len(unique_tags)} unique tags.")
            return unique_tags
        else:
            print(f"Warning: No lists found containing 'list_for_freeform_' at {url}")
            return []
    except Exception as e:
        print(f"An error occurred while scraping {url}: {e}")
        return []
    
def main():
    print("Attempting to bypass Cloudflare (this may take a moment)...")
    
    # Create a scraper instance that mimics a real browser
    scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False})

    new_scraped_data = {}
    for key, url in URLS.items():
        new_scraped_data[key] = scrape_url(scraper, url)

    valid_scraped_tags_pool = set(new_scraped_data["all"] + new_scraped_data["round_specific"])
    
    organized = {
        "all": new_scraped_data["all"],
        "round_specific": new_scraped_data["round_specific"]
    }

    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)

            for key, value in existing_data.items():
                if key not in ["all", "round_specific"]:
                    if isinstance(value, list):
                        # Keep the tag ONLY if it still exists in the scraped tags pool
                        cleaned_tags = [tag for tag in value if tag in valid_scraped_tags_pool]
                        
                        removed_count = len(value) - len(cleaned_tags)
                        if removed_count > 0:
                            print(f"Cleaned category '{key}': Removed {removed_count} stale tags.")
                            
                        organized[key] = cleaned_tags
                    else:
                        # Fallback
                        organized[key] = value

            print(f"Preserved custom categories: {[k for k in existing_data.keys() if k not in ['all', 'round_specific']]}")
        except Exception as read_error:
            print(f"Critical Error: Failed to safely parse existing file. Aborting write to save data. Error: {read_error}")
            return # Return so file isn't overwritten

    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(organized, f, indent=4, ensure_ascii=False)
        print("Successfully updated search/tags.json file!")
    except Exception as write_error:
        print(f"Error saving JSON file: {write_error}")


if __name__ == "__main__":
    main()
