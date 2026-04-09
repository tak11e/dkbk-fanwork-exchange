import cloudscraper
from bs4 import BeautifulSoup
import json
import re
import collections
import math


# Your specific Tag Set URL
url = "https://archiveofourown.org/tag_sets/28436"

# Train our algorithm by providing examples
training_data = {
    "nsfw": [
        "Accidental Bondage",
        "Agency locker room public sex",
        "Aizawa Shouta walks in on them",
        "and they fuck like rabbits",
        "Armpit Kink",
        "Ass kissing but it’s the good kind",
        "Attending a fancy party and getting obnoxiously horny about it",
        "Bakugou Katsuki babytraps Midoriya Izuku intermediate Midoriya Izuku pokes holes in the condoms",
        "Bakugou Katsuki has a big useless dick because he's a bottom",
        "Bakugou Katsuki has a micropenis",
        "Bakugou Katsuki Has a Rainforest Pussy",
        "Bakugou Katsuki Has a Voice Kink",
        "Bakugou Katsuki has heart eyes when he cums",
        "Bakugou Katsuki is a squirter",
        "Bakugou Katsuki is built for backshots",
        "Bakugou Katsuki is used and treated like a fleshlight",
        "Bakugou Katsuki looks good with handprints on his ass",
        "bakugou katsuki loves being choked into unconsciousness",
        "Bakugou Katsuki swears he’s not into being manhandled",
        "biting as foreplay",
        "Bakugou Katsuki uses Midoriya Izuku like a dildo",
    ],
    "sfw": [
        "Autistic Bakugou Katsuki",
        "Bakugou Katsuki flirts with Midoriya Izuku in front of his class and only his students seem to notice",
        "Bakugou Katsuki getting the princess treatment he deserves"
    ]
}

def train_classifier(data):
    vocabulary = set()
    word_counts = {"nsfw": collections.defaultdict(int), "sfw": collections.defaultdict(int)}
    class_counts = {"nsfw": len(data["nsfw"]), "sfw": len(data["sfw"])}

    for label, tags in data.items():
        for tag in tags:
            for word in tag.lower().split():
                vocabulary.add(word)
                word_counts[label][word] += 1
    return vocabulary, word_counts, class_counts

vocab, counts, classes = train_classifier(training_data)

def classify_tag(new_tag):
    new_tag_words = new_tag.lower().split()
    total_tags = classes["nsfw"] + classes["sfw"]

    # Starting probabilities
    log_probs = {
        "nsfw": math.log(classes["nsfw"] / total_tags),
        "sfw": math.log(classes["sfw"] / total_tags)
    }

    for label in ["nsfw", "sfw"]:
        total_words_in_class = sum(counts[label].values())
        for word in new_tag_words:
            # Probability of word given class
            word_prob = (counts[label][word] + 1) / (total_words_in_class + len(vocab))
            log_probs[label] += math.log(word_prob)

    return "nsfw" if log_probs["nsfw"] > log_probs["sfw"] else "sfw"


# def get_categorized_data(all_tags):
#     groups = {
#         "au": ["alternate universe", " au", "canon divergence"],
#         "nsfw": ["nsfw", "sex", "anal", "fingering", "pussy", "cock", "kink", "heat", "walks in", "fuck", "bondage", "ass", "horny", "condom", "dick", "penis", "cum", "squirt", "backshot", "fleshlight", "choke", "manhandle", "manhandling", "dildo", "buttplug", "lingerie", "foreplay", "strap", "concubine", "dacryphilia", "frot", "dry humping", "balls deep", "lust", "macro", "micro", "mating", "in bed", "gets hard", "turned on", "sperm", "yaoi", ""],
#         "angst": []
#         "dddne": ["dead dove", "blood", "violence", "trauma", ]
#         "silly"
#         "sfw": ["non-sexual"]
#     }

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

            # Dynamic sorting logic
            organized = {
                "all": unique_tags,
                "nsfw": [],
                "sfw": []
            }

            for tag in unique_tags:
                tag_lower = tag.lower()

                category = classify_tag(tag)
                organized[category].append(tag)
            
            with open('tags.json', 'w') as f:
                json.dump(organized, f, indent=4)
            
            print(f"Success! Found {len(freeform_lists)} separate lists.")
            print(f"Total unique tags saved: {len(unique_tags)}")
            print(f"Total NSFW tags saved: {len(organized.nsfw)}")
            print(f"Total SFW tags saved: {len(organized.sfw)}")
        else:
            print("Error: No lists found containing 'list_for_freeform_'.")
            
    except Exception as e:
        print(f"An error occured: {e}")

if __name__ == "__main__":
    get_tags()
