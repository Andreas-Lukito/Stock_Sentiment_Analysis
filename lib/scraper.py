from genericpath import exists
from dotenv import load_dotenv
import json
import os
import re
import requests
from typing import Any
from newspaper import Article

load_dotenv()

api_token = os.getenv("API_TOKEN")

def get_cached_news_metadata(page: int = 1, before_date: str = "2025-09", path : str = ".") -> Any:
    """
    This function is to fetch news metadata before the `before_date` with caching
    
    :param:
        page (int): the number of news articles you want to scrape

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
        with open(os.path.join(path, f"news_cache/{before_date}/page-{page}.json"), "r") as cache:
            content =  cache.read()
            return json.loads(content)
        
    except:
        res: requests.Response = requests.get(
            "https://api.marketaux.com/v1/news/all",
            params={
                "api_token": api_token,
                "published_before": before_date,
                "page": page,
                "language": "en"
            }
        )

        result = res.json()

        if res.status_code != 200:
            raise ConnectionRefusedError("Return status not OK")

        # Make sure the directory exists
        os.makedirs(os.path.join(path, f"news_cache/{before_date}/"), exist_ok = True)

        try:
            with open(os.path.join(path, f"news_cache/{before_date}/page-{page}.json"), "w") as new_cache:
                new_cache.write(json.dumps(result))
        
        except:
            print("Error when writing cache!")

        return result

if __name__ == "__main__":
    print(get_cached_news_metadata(page=2))