"""
Fetches posts from r/unpopularopinion via RSS (regular + certified flair).
Labels each post on the fly and writes incrementally to:
  - data/raw_posts.json  (full post data with label)
  - data/posts.csv       (text + label only)
"""

import requests
import feedparser
import time
import json
import csv
import re
from bs4 import BeautifulSoup
from pathlib import Path

HEADERS = {'User-Agent': 'Mozilla/5.0 (compatible; research-bot/1.0)'}
DATA_DIR = Path(__file__).parent.parent / "data"
JSON_FILE = DATA_DIR / "raw_posts.json"
CSV_FILE = DATA_DIR / "posts.csv"

SOURCES = [
    {
        'name': 'regular',
        'rss': 'https://www.reddit.com/r/unpopularopinion/.rss',
        'target': 25
    },
    {
        'name': 'certified',
        'rss': 'https://www.reddit.com/r/unpopularopinion/.rss?f=flair_name%3A%22%3Aredditgold%3ACertified%20Unpopular%20Opinion%3Aredditgold%3A%22',
        'target': 25
    }
]

# --- Labeling ---

WILD_TAKES_PATTERNS = [
    r'\beveryone (should|needs? to|ought to|must|capable)\b',
    r'\ball (people|humans|adults|men|women) should\b',
    r'\bshould be (required|mandatory|normal|standard)\b',
    r'\btry (eating|doing|living|going|sitting|standing)\b',
    r'\beveryone (should|needs?) (try|experience|do|see|watch|eat|visit)\b',
    r'\byou should (try|do|experience|eat|visit|watch)\b',
]

SALT_POST_PATTERNS = [
    r'\b(hate|hates|hated|hating)\b',
    r'\b(annoying|annoys|annoy|annoyed)\b',
    r'\b(frustrat(ing|ed|es|ion))\b',
    r'\b(sucks?|suck|sucked)\b',
    r'\b(awful|terrible|horrible|atrocious)\b',
    r'\b(worst|the worst)\b',
    r'\b(ruins?|ruined|destroying|destroys)\b',
    r'\b(drives? me (crazy|nuts|insane))\b',
    r"\bcan't stand\b",
    r'\bstop (doing|saying|being|acting|pretending)\b',
    r'\btired of\b',
    r'\bsick of\b',
    r'\boverrated\b',
]

ALTERNATIVE_PERSPECTIVE_PATTERNS = [
    r'\bactually (good|great|fine|better|not|okay|decent|wonderful|underrated)\b',
    r'\bnot (as|that) (bad|hard|difficult|good|great|easy|simple|complicated)\b',
    r'\bcontrary to\b',
    r'\bmisconception\b',
    r'\bwrong (idea|about|way|impression)\b',
    r'\bpeople (have|think|believe|assume|forget|ignore|overlook)\b',
    r'\beveryone (thinks|believes|assumes|forgets|ignores)\b',
    r'\bnot what (people|everyone|most)\b',
    r'\bunderrated\b',
    r'\breframe\b',
    r'\bdifferent (way|perspective|view|angle)\b',
    r'\bopposite (of|effect|is true)\b',
    r'\bnot (the|a) (curse|burden|problem|issue|disaster)\b',
    r'\bbiggest lie\b',
    r'\bactually (is|are|isn\'t|aren\'t|was|were)\b',
]


def label_post(title, text):
    combined = (title + ' ' + text).lower()

    # Wild takes: unconventional suggestions everyone should try
    for pat in WILD_TAKES_PATTERNS:
        if re.search(pat, combined):
            return 'wild-takes'

    # Salt-post: frustration / complaining
    salt_hits = sum(1 for pat in SALT_POST_PATTERNS if re.search(pat, combined))
    if salt_hits >= 2:
        return 'salt-post'

    # Alternative perspective: reframes a common view
    for pat in ALTERNATIVE_PERSPECTIVE_PATTERNS:
        if re.search(pat, combined):
            return 'alternative-perspective'

    # Single salt hit still counts
    if salt_hits == 1:
        return 'salt-post'

    # Default: restating something most people already believe
    return 'restating-the-obvious'


# --- Fetching ---

def fetch_page(base_rss, after=None):
    if after:
        sep = '&' if '?' in base_rss else '?'
        url = base_rss + f"{sep}after={after}"
    else:
        url = base_rss
    time.sleep(3)
    resp = requests.get(url, headers=HEADERS, timeout=15)
    if resp.status_code == 429:
        print("  Rate limited, waiting 60s...")
        time.sleep(60)
        resp = requests.get(url, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    return feedparser.parse(resp.content)


def fetch_post_body(post_url):
    rss_url = post_url.rstrip('/') + '.rss'
    time.sleep(2)
    try:
        resp = requests.get(rss_url, headers=HEADERS, timeout=15)
        if resp.status_code == 429:
            time.sleep(60)
            resp = requests.get(rss_url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        feed = feedparser.parse(resp.content)
        if feed.entries and 'summary' in feed.entries[0]:
            soup = BeautifulSoup(feed.entries[0].summary, 'html.parser')
            raw = soup.get_text(strip=True, separator='\n')
            paragraphs = [p.strip() for p in raw.split('\n\n') if p.strip()]
            return '\n\n'.join(paragraphs[:5])
    except Exception as e:
        print(f"    Error fetching body: {e}")
    return ""


def collect_from_source(source, json_file, csv_writer, seen_ids, is_first_entry):
    base_rss = source['rss']
    target = source['target']
    name = source['name']
    collected = 0
    after = None

    while collected < target:
        print(f"[{name}] Fetching page... ({collected}/{target})")
        feed = fetch_page(base_rss, after)

        if not feed.entries:
            print(f"[{name}] No more entries.")
            break

        for entry in feed.entries:
            post_id = entry.get('id', '')
            if not post_id or post_id in seen_ids:
                continue
            seen_ids.add(post_id)

            title = entry.get('title', '').replace('&amp;', '&')
            link = entry.get('link', '')

            if not link or '/comments/' not in link:
                continue

            print(f"  [{name}] {title[:70]}...")
            body = fetch_post_body(link)

            text = title
            if body and len(body) > 20:
                text = f"{title}\n\n{body}"

            label = label_post(title, text)
            print(f"    -> {label}")

            post = {'id': post_id, 'title': title, 'url': link,
                    'text': text, 'label': label, 'source': name}

            # Write to JSON array incrementally
            if not is_first_entry[0]:
                json_file.write(',\n')
            json_file.write('  ' + json.dumps(post))
            json_file.flush()
            is_first_entry[0] = False

            # Write to CSV immediately
            csv_writer.writerow({'text': text, 'label': label})

            collected += 1
            if collected >= target:
                break

        # Paginate
        last_id = feed.entries[-1].get('id', '') if feed.entries else ''
        if last_id.startswith('t3_'):
            after = last_id
        elif '/comments/' in last_id:
            short = last_id.split('/comments/')[1].split('/')[0]
            after = f"t3_{short}"
        else:
            print(f"[{name}] Cannot paginate from id: {last_id}")
            break

    return collected


if __name__ == "__main__":
    DATA_DIR.mkdir(exist_ok=True)
    seen_ids = set()
    total = 0
    is_first_entry = [True]

    with open(JSON_FILE, 'w') as jf, open(CSV_FILE, 'w', newline='') as cf:
        csv_writer = csv.DictWriter(cf, fieldnames=['text', 'label'])
        csv_writer.writeheader()
        cf.flush()

        jf.write('[\n')

        for i, source in enumerate(SOURCES):
            if i > 0:
                print("Waiting 30s before next source to avoid rate limiting...")
                time.sleep(30)
            n = collect_from_source(source, jf, csv_writer, seen_ids, is_first_entry)
            total += n
            print(f"\n[{source['name']}] Collected {n} posts.\n")

        jf.write('\n]')

    print(f"Done. {total} posts -> {JSON_FILE} + {CSV_FILE}")
