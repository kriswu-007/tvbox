"""Simple Douban Top250 spider with resilient parsing.

The script scrapes Douban's Top250 list and demonstrates safer handling
of optional fields to avoid ``IndexError`` when a regex match is missing.
"""

import re
import time
from dataclasses import dataclass, asdict
from typing import List

import requests
from bs4 import BeautifulSoup

# Base URL used for pagination
BASE_URL = "https://movie.douban.com/top250?start="

# Regular expressions reused across items
FIND_LINK = re.compile(r'<a href="(.*?)">')
FIND_IMG_SRC = re.compile(r'<img.*src="(.*?)"', re.S)
FIND_TITLE = re.compile(r'<span class="title">(.*?)</span>')
FIND_RATING = re.compile(r'<span class="rating_num".*>(.*)</span>')
FIND_EVALUATE = re.compile(r'<span>(\d*)人评价</span>')
FIND_INQ = re.compile(r'<span class="inq">(.*)</span>')
FIND_BD = re.compile(r'<p class="">(.*?)</p>', re.S)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}


@dataclass
class Movie:
    """Container for a single movie entry."""

    title: str
    other_title: str
    link: str
    img_src: str
    rating: str
    evaluate: str
    inq: str
    bd: str


def ask_url(url: str) -> str:
    """Fetch the HTML for a given URL using a browser-like header."""

    response = requests.get(url, headers=HEADERS, timeout=10)
    response.raise_for_status()
    response.encoding = response.apparent_encoding
    return response.text


def safe_first_match(pattern: re.Pattern[str], text: str, default: str = "") -> str:
    """Return the first regex match or a default value when missing."""

    matches = pattern.findall(text)
    if not matches:
        return default
    return matches[0].strip()


def parse_item(item_html: str) -> Movie:
    """Parse a single movie block into a ``Movie`` instance."""

    link = safe_first_match(FIND_LINK, item_html)
    img_src = safe_first_match(FIND_IMG_SRC, item_html)

    titles = FIND_TITLE.findall(item_html)
    title = titles[0].strip() if titles else ""
    other_title = titles[1].replace("/", "").strip() if len(titles) > 1 else ""

    rating = safe_first_match(FIND_RATING, item_html)
    evaluate = safe_first_match(FIND_EVALUATE, item_html)
    inq = safe_first_match(FIND_INQ, item_html)

    bd_raw = safe_first_match(FIND_BD, item_html)
    bd_clean = re.sub(r"<br\s*/?>", " ", bd_raw)
    bd_clean = re.sub(r"/", " ", bd_clean).strip()

    return Movie(
        title=title,
        other_title=other_title,
        link=link,
        img_src=img_src,
        rating=rating,
        evaluate=evaluate,
        inq=inq,
        bd=bd_clean,
    )


def get_data(base_url: str = BASE_URL, pages: int = 10) -> List[Movie]:
    """Collect movie data across the Top250 pages.

    Args:
        base_url: Base Douban URL without pagination offset.
        pages: Number of 25-item pages to fetch (default 10 for full Top250).

    Returns:
        A list of :class:`Movie` objects.
    """

    all_movies: List[Movie] = []
    for i in range(pages):
        url = f"{base_url}{i * 25}"
        html = ask_url(url)
        soup = BeautifulSoup(html, "html.parser")
        for item in soup.find_all("div", class_="item"):
            movie = parse_item(str(item))
            all_movies.append(movie)
        time.sleep(0.2)
    return all_movies


# Preserve the legacy camelCase API for downstream scripts while keeping
# the newer snake_case implementations above. This ensures older imports
# like ``getData`` continue to work without modification.
def askURL(url: str) -> str:  # noqa: N802
    return ask_url(url)


def getData(baseurl: str = BASE_URL) -> List[Movie]:  # noqa: N802
    return get_data(baseurl)


def main():
    movies = get_data()
    for movie in movies:
        print(asdict(movie))


if __name__ == "__main__":
    main()
