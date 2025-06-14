import requests
from bs4 import BeautifulSoup

def scrape_titles_yahoo_business(url: str) -> list:
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    titles = []
    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        if (
            "news.yahoo.co.jp/articles/" in href or
            "news.yahoo.co.jp/pickup/" in href
        ):
            text = a_tag.get_text(strip=True)
            if text:
                titles.append(text)

    return list(set(titles))