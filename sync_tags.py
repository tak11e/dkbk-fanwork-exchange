import cloudscraper
from bs4 import BeautifulSoup
import json
import re

# Your specific Tag Set URL
url = "https://archiveofourown.org/tag_sets/28436"

def get_tags():
    print("Attempting to bypass Cloudflare (this may take a moment)...")
    
    # Create a scraper instance that mimics a real browser
    scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False})
    
    try:
        response = scraper.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        all_tags = []

        freeform_lists = soup.find_all('ol', id=re.compile(r'list_for_freeform'))
        
        if freeform_lists:
            for lst in freeform_lists:
                tags = [li.get_text(strip=True) for li in lst.find_all('li')]
                all_tags.extend(tags)
            
            unique_tags = list(dict.fromkeys(all_tags))
            
            with open('tags.json', 'w') as f:
                json.dump(unique_tags, f, indent=4)
            
            print(f"Success! Found {len(freeform_lists)} separate lists.")
            print(f"Total unique tags saved: {len(unique_tags)}")
        else:
            print("Error: No lists found containing 'list_for_freeform_'.")
            
    except Exception as e:
        print(f"An error occured: {e}")

if __name__ == "__main__":
    get_tags()
