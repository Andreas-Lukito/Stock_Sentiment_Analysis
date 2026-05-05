from dotenv import load_dotenv
import json
import os
import re
import requests
import threading
from typing import Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from newspaper import Article
import cloudscraper
import random
import time
import pandas as pd
from tqdm import tqdm
from IPython.display import clear_output
import threading
_local = threading.local()

load_dotenv()

api_token = os.getenv("API_TOKEN")

def get_cached_news_metadata_before_date(page: int = 1, before_date: str = "2025-09", path: str = ".") -> Any:
    """
    This function is to fetch news metadata before the `before_date` with caching
    
    :param:
        page (int): the page of the news article you want to scrape

        before_date (str): The articles you want to get before `before_date`

        path (str): Your path location
    """

    if not api_token:
        raise RuntimeError("API key not found")

    valid_date_pattern = r"^[0-9]{4}\-(0[1-9]|1[0-2])$"
    match = re.search(valid_date_pattern, before_date)

    if not match:
        raise ValueError("Date must be of format Y-m")
    
    try:
        with open(os.path.join(path, f"news_cache/before_date/{before_date}/json/page-{page}.json"), "r") as cache:
            content =  cache.read()
            return json.loads(content)
        
    except:
        res: requests.Response = requests.get(
            "https://api.marketaux.com/v1/news/all",
            params={
                "api_token": api_token,
                "published_before": before_date,
                "page": page,
                # Scraper to get neutral scores
                "sentiment_lte": 0,
                "sentiment_gte": 0,

                # Scraper to get negative scores
                # "sentiment_lte": -0.5,

                # Scraper to get positive scores
                # "sentiment_gte": 0.5,
                "language": "en"
            }
        )

        result = res.json()

        if res.status_code != 200:
            raise ConnectionRefusedError("Return status not OK")

        # Make sure the directory exists
        os.makedirs(os.path.join(path, f"news_cache/before_date/{before_date}/json/"), exist_ok = True)

        try:
            with open(os.path.join(path, f"news_cache/before_date/{before_date}/json/page-{page}.json"), "w") as new_cache:
                new_cache.write(json.dumps(result))
        
        except:
            print("Error when writing cache!")

        return result

def get_cached_news_metadata_after_date(page: int = 1, after_date: str = "2025-09", path: str = ".") -> Any:
    """
    This function is to fetch news metadata before the `after_date` with caching
    
    :param:
        page (int): the page of the news article you want to scrape

        after_date (str): The articles you want to get before `after_date`

        path (str): Your path location
    """

    if not api_token:
        raise RuntimeError("API key not found")

    valid_date_pattern = r"^[0-9]{4}\-(0[1-9]|1[0-2])$"
    match = re.search(valid_date_pattern, after_date)

    if not match:
        raise ValueError("Date must be of format Y-m")
    
    try:
        print(f"Reading cache at: {os.path.join(path, f'news_cache/after_date/{after_date}/json/page-{page}.json')}") # debug purposes
        with open(os.path.join(path, f"news_cache/after_date/{after_date}/json/page-{page}.json"), "r") as cache:
            content =  cache.read()
            return json.loads(content)
        
    except:
        res: requests.Response = requests.get(
            "https://api.marketaux.com/v1/news/all",
            params={
                "api_token": api_token,
                "published_after": after_date,
                "page": page,
                # Scraper to get neutral scores
                "sentiment_lte": 0,
                "sentiment_gte": 0,

                # Scraper to get negative scores
                # "sentiment_lte": -0.5,

                # Scraper to get positive scores
                # "sentiment_gte": 0.5,
                "language": "en"
            }
        )

        result = res.json()

        if res.status_code != 200:
            raise ConnectionRefusedError(f"Return status not OK with code {res.status_code}")

        # Make sure the directory exists
        os.makedirs(os.path.join(path, f"news_cache/after_date/{after_date}/json/"), exist_ok = True)

        try:
            with open(os.path.join(path, f"news_cache/after_date/{after_date}/json/page-{page}.json"), "w") as new_cache:
                print(f"wrote cache at: {os.path.join(path, f'news_cache/after_date/{after_date}/json/page-{page}.json')}") # debug purposes
                new_cache.write(json.dumps(result))
                
        
        except:
            print("Error when writing cache!")

        return result

# Create scraper with better browser emulation
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",

    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0",

    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.3 Safari/605.1.15",

    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
]

def get_realistic_headers(url: str, user_agent: str) -> dict:
    """Build a full, realistic browser header set."""
    from urllib.parse import urlparse
    origin = f"{urlparse(url).scheme}://{urlparse(url).netloc}"

    return {
        "User-Agent": user_agent,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",       # "none" = typed URL / bookmark
        "Sec-Fetch-User": "?1",
        "Sec-CH-UA": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
        "Sec-CH-UA-Mobile": "?0",
        "Sec-CH-UA-Platform": '"Windows"',
        "Cache-Control": "max-age=0",
        "Referer": origin,              # looks like you navigated from the same site
    }

def get_scraper():
    """One cloudscraper instance per thread."""
    if not hasattr(_local, "scraper"):
        _local.scraper = cloudscraper.create_scraper(
            browser={"browser": "chrome", "platform": "windows", "mobile": False}
        )
    return _local.scraper

def human_delay(min_s: float = 2.0, max_s: float = 6.0):
    """Sleep for a random duration with a slight gaussian skew."""
    base = random.uniform(min_s, max_s)
    jitter = random.gauss(0, 0.4)
    time.sleep(max(min_s, base + jitter))

def extract_text_from_url(url: str, timeout: int = 30, retries: int = 3) -> str:
    """
    Extract article text using cloudscraper + newspaper3k,
    with realistic headers, delays, and retry logic.
    """
    user_agent = random.choice(USER_AGENTS)
    headers = get_realistic_headers(url, user_agent)

    # Warm up: visit the homepage first to get cookies (like a real browser would)
    try:
        from urllib.parse import urlparse
        homepage = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
        scraper = get_scraper()
        scraper.get(homepage, headers=headers, timeout=timeout)
        human_delay(1.5, 3.5)   # pause between homepage → article
    except Exception:
        pass  # non-fatal, continue anyway

    last_error = None
    for attempt in range(1, retries + 1):
        try:
            human_delay()   # delay before every attempt

            scraper = get_scraper()
            response = scraper.get(url, headers=headers, timeout=timeout)

            if response.status_code == 403:
                raise Exception("403 Forbidden - bot detection triggered")
            if response.status_code == 429:
                wait = 10 * attempt          # back off harder each retry
                print(f"Rate limited. Waiting {wait}s before retry {attempt}…")
                time.sleep(wait)
                continue
            if response.status_code != 200:
                raise Exception(f"Bad response: {response.status_code}")

            article = Article(url)
            article.set_html(response.text)
            article.parse()

            if not article.text.strip():
                raise Exception("Parsed article text is empty")

            return article.text

        except Exception as e:
            last_error = e
            if attempt < retries:
                backoff = 5 * attempt
                print(f"Attempt {attempt} failed: {e}. Retrying in {backoff}s…")
                time.sleep(backoff)

    raise Exception(f"All {retries} attempts failed for: {url}\nLast error: {last_error}")

def safe_extract_row(row) -> str:
    """
    Wraps extract_text_from_url for a full dataframe row.
    Falls back to title+description+snippet if URL is missing or scraping fails.
    """
    url = row["url"]
    fallback = f"{row['title']} {row['description']} {row['snippet']}"

    # --- invalid URL: skip scraping entirely ---
    if pd.isna(url) or not isinstance(url, str) or url.strip() == "":
        tqdm.write(f"Invalid URL, using fallback | {url}")
        return fallback

    # --- try scraping ---
    try:
        text = extract_text_from_url(url)

        if not text or text.strip() == "":
            raise ValueError("Empty scraped text")

        tqdm.write(f"✓ {url}")
        return text

    except Exception as e:
        tqdm.write(f"Failed ({e}), using fallback | {url}")
        return fallback

def scrape_dataframe(
    df: pd.DataFrame,
    url_col: str = "url",
    text_col: str = "text",
    max_workers: int = 5,
    batch_size: int = 200,
    output_path: str = "news_scraped.csv",
) -> pd.DataFrame:

    # --- resume from checkpoint if available ---
    if os.path.exists(output_path):
        print(f"Resuming from checkpoint: {output_path}")
        checkpoint_df = pd.read_csv(output_path)
        scraped_uuids = set(checkpoint_df["uuid"].tolist())
        remaining = df[~df["uuid"].isin(scraped_uuids)].copy()
        print(f"  {len(scraped_uuids)} done, {len(remaining)} remaining")
    else:
        checkpoint_df = pd.DataFrame()
        remaining = df.copy()

    if remaining.empty:
        print("All rows already scraped!")
        # reconstruct full df from checkpoint preserving original column order
        return checkpoint_df[df.columns]

    rows = [row for _, row in remaining.iterrows()]
    total_batches = (len(rows) + batch_size - 1) // batch_size
    print(f"Scraping {len(rows)} rows across {total_batches} batches...")
``
    for batch_num, start in enumerate(range(0, len(rows), batch_size), 1):
        clear_output(wait=True)
        batch_rows = rows[start : start + batch_size]
        print(f"\nBatch {batch_num}/{total_batches} ({len(batch_rows)} rows)")

        batch_results = {}
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_row = {
                executor.submit(safe_extract_row, row): row
                for row in batch_rows
            }
            for future in tqdm(
                as_completed(future_to_row),
                total=len(batch_rows),
                desc=f"Batch {batch_num}"
            ):
                row = future_to_row[future]
                batch_results[row["uuid"]] = future.result()

        # map results back
        batch_df = pd.DataFrame(batch_rows)
        batch_df[text_col] = batch_df["uuid"].map(batch_results)

        # append batch to checkpoint and save
        checkpoint_df = pd.concat([checkpoint_df, batch_df], ignore_index=True)
        checkpoint_df.to_csv(output_path, index=False)

        n_scraped = sum(
            1 for r in batch_rows
            if batch_results.get(r["uuid"], "") != f"{r['title']} {r['description']} {r['snippet']}"
        )
        n_fallback = len(batch_rows) - n_scraped
        print(f"  ✓ {n_scraped} scraped, ↩ {n_fallback} fallback — saved to {output_path}")

    return checkpoint_df[df.columns]

if __name__ == "__main__":
    print(get_cached_news_metadata_before_date(page=2))