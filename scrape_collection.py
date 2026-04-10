import cloudscraper
from bs4 import BeautifulSoup
import json
import os
import time
import re

OLD_COLLECTION_URL = "https://archive.transformativeworks.org/collections/dkbk_exchange/works"

def scrape_all_pages(total_pages=13):
    scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'windows'})
    scraper.cookies.set("view_adult", "true", domain="archiveofourown.org")
    
    organized = {
        "nsfw": {"art": [], "fic": []},
        "sfw": {"art": [], "fic": []}
    }

    for page_num in range(1, total_pages + 1):
        url = f"{OLD_COLLECTION_URL}?page={page_num}"
        print(f"Scraping page {page_num}...")

        try:
            response = scraper.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            found_on_page = 0
            for h4 in soup.find_all('h4', class_='heading'):
                link = h4.find('a', href=True)
                if link and '/works/' in link['href']:
                    blurb = h4.find_parent('li')
                    if not blurb: continue

                    work_url = "https://archiveofourown.org" + link['href']
                    print(f"    -> Deep scraping: {link.get_text(strip=True)}")

                    word_count_el = blurb.select_one('dd.words')
                    word_count = int(word_count_el.get_text().replace(',', '')) if word_count_el and word_count_el.get_text().strip() else 0

                    tag_elements = blurb.select('ul.tags li a.tag')
                    tags_list = [t.get_text(strip=True) for t in tag_elements]
                    tags_as_string = " ".join(tags_list).lower()

                    time.sleep(5)

                    img_url = ""
                    try:
                        work_res = scraper.get(work_url)
                        work_soup = BeautifulSoup(work_res.text, 'html.parser')

                        content_img = work_soup.select_one('#chapters img, .userstuff img, .work-content img')
                        if content_img:
                            img_url = content_img.get('src', '')
                    except Exception as e:
                        print(f"    ! Cound not load work page: {e}")
                    
                    summary_box = blurb.select_one('blockquote.userstuff')

                    work_data = {
                        "title": link.get_text(strip=True),
                        "url": work_url,
                        "summary": summary_box.get_text(strip=True) if summary_box else "No summary provided.",
                        "tags": [t.get_text(strip=True) for t in tag_elements],
                        "image": img_url if img_url else "No image provided.",
                        "last_featured": ""
                    }

                    rating_icon = blurb.select_one('.rating')
                    rating_text = rating_icon.get('title', '') if rating_icon else ""

                    is_nsfw = any(word in rating_text for word in ["Explicit", "Mature"])
                    rating_key = "nsfw" if is_nsfw else "sfw"

                    is_art_tag = bool(re.search(r'\b(art|fanart)\b', tags_as_string))
                    is_art = is_art_tag or (img_url != "" and word_count < 100)
                    
                    type_key = "art" if is_art else "fic"

                    organized[rating_key][type_key].append(work_data)
                    found_on_page += 1

            print(f"    -> Found {found_on_page} works.")

            # Wait 5 seconds between pages to avoid AO3 ban
            time.sleep(5)

        except Exception as e:
            print(f"Error on page {page_num}: {e}")
            break
        
    with open('collection_works.json', 'w') as f:
        json.dump(organized, f, indent=4)
    print(f"Saved {len(organized['nsfw']['art'] + organized['sfw']['art'] + organized['nsfw']['fic'] + organized['sfw']['fic'])} works across {total_pages} pages.")

if __name__ == "__main__":
    scrape_all_pages(13)