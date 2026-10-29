"""
Web Scraper for books.toscrape.com
----------------------------------
Task 29: Create a Web Scraping Program (Level 1, Day 29)

A simple, robust web scraping script demonstrating:
1. robots.txt parsing and permission checking with urllib.robotparser.
2. HTTP requests with custom User-Agent, timeouts, and error handling.
3. Polite rate-limiting using time delays.
4. HTML parsing and element extraction with BeautifulSoup (bs4).
5. Saving structured data to CSV with UTF-8 encoding.
6. Clean terminal summary reporting and data analysis.

Author: Hemasri Malla
Target: https://books.toscrape.com/ (Sandbox site for scraping practice)
"""

import csv
import os
import re
import sys
import time
import urllib.robotparser
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

# Ensure Windows terminal prints UTF-8 characters (like £) properly
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Determine output file path in the same directory as this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CSV_PATH = os.path.join(BASE_DIR, "books_data.csv")

# Star rating conversion mapping (textual rating -> integer)
RATING_MAP = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
}

# Standard polite User-Agent for this educational scraper
DEFAULT_USER_AGENT = (
    "BookScraperBot/1.0 (+https://github.com/hemasrimalla/web-scraper; "
    "educational practice)"
)


def check_robots_allowed(url: str, user_agent: str = DEFAULT_USER_AGENT) -> bool:
    """
    Fetches and checks the site's robots.txt rules using urllib.robotparser.

    Parameters:
        url (str): The page URL to check permission for.
        user_agent (str): The User-Agent string to check rules against.

    Returns:
        bool: True if fetching the URL is permitted by robots.txt, False otherwise.
    """
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    print(f"[*] Checking robots.txt at: {robots_url}")

    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(robots_url)

    try:
        rp.read()
        allowed = rp.can_fetch(user_agent, url)
        if allowed:
            print(f"[+] robots.txt allows access to '{url}' for User-Agent: '{user_agent}'.")
        else:
            print(f"[-] robots.txt DISALLOWS access to '{url}' for User-Agent: '{user_agent}'.")
        return allowed
    except Exception as exc:
        print(f"[!] Warning: Could not retrieve/parse robots.txt ({exc}). Proceeding politely.")
        # If robots.txt returns 404 or cannot be read, web conventions treat paths as allowed
        return True


def fetch_page(url: str, headers: dict | None = None, timeout: int = 10) -> str | None:
    """
    Sends an HTTP GET request to retrieve a webpage's HTML text.

    Parameters:
        url (str): The web page URL to fetch.
        headers (dict, optional): Custom HTTP headers (e.g. User-Agent).
        timeout (int): Request timeout in seconds.

    Returns:
        str | None: Raw HTML content string if successful, or None if an error occurs.
    """
    if headers is None:
        headers = {"User-Agent": DEFAULT_USER_AGENT}

    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()

        # Ensure correct UTF-8 encoding so currency symbols (e.g. £) render cleanly
        response.encoding = response.apparent_encoding or "utf-8"
        return response.text

    except requests.exceptions.Timeout:
        print(f"[!] Timeout Error: The request exceeded {timeout} seconds for {url}")
    except requests.exceptions.ConnectionError:
        print(f"[!] Connection Error: Failed to connect to {url}")
    except requests.exceptions.HTTPError as http_err:
        status = getattr(response, "status_code", "Unknown")
        print(f"[!] HTTP Error: Status code {status} returned by {url} ({http_err})")
    except requests.exceptions.RequestException as req_err:
        print(f"[!] Request Error: An unexpected error occurred: {req_err}")

    return None


def parse_books(html_content: str, base_url: str) -> list[dict]:
    """
    Parses book listing cards from HTML and extracts structured data.

    Parameters:
        html_content (str): The raw HTML source code of the catalog page.
        base_url (str): The page URL used to resolve relative book hyperlinks.

    Returns:
        list[dict]: A list of dictionaries representing extracted books.
    """
    books = []
    soup = BeautifulSoup(html_content, "html.parser")

    # Each book is contained in an <article class="product_pod"> tag
    product_cards = soup.find_all("article", class_="product_pod")

    for pod in product_cards:
        # 1. Title & Product URL: Found inside <h3><a href="..." title="...">...</a></h3>
        title = "Unknown Title"
        product_url = ""
        h3_tag = pod.find("h3")
        if h3_tag:
            a_tag = h3_tag.find("a")
            if a_tag:
                # The 'title' attribute holds the complete title (the anchor text is often truncated with '...')
                title = a_tag.get("title") or a_tag.get_text(strip=True) or "Unknown Title"
                rel_href = a_tag.get("href", "")
                if rel_href:
                    product_url = urljoin(base_url, rel_href)

        # 2. Price: Found inside <p class="price_color">
        price_elem = pod.find("p", class_="price_color")
        price = price_elem.get_text(strip=True) if price_elem else "£0.00"
        # Remove any stray encoding artifacts like 'Â' before '£'
        price = price.replace("Â", "").strip()

        # 3. Star Rating: Found in class attribute of <p class="star-rating <RatingWord>">
        star_rating = 0
        rating_elem = pod.find("p", class_="star-rating")
        if rating_elem and rating_elem.get("class"):
            for cls in rating_elem.get("class"):
                cls_lower = cls.lower()
                if cls_lower in RATING_MAP:
                    star_rating = RATING_MAP[cls_lower]
                    break

        # 4. Availability: Found inside <p class="instock availability">
        avail_elem = pod.find("p", class_="availability")
        availability = avail_elem.get_text(strip=True) if avail_elem else "Unknown"

        books.append({
            "title": title,
            "price": price,
            "star_rating": star_rating,
            "availability": availability,
            "product_url": product_url,
        })

    return books


def save_to_csv(books: list[dict], filename: str = DEFAULT_CSV_PATH) -> bool:
    """
    Saves a list of book dictionaries into a CSV file with UTF-8 encoding.

    Parameters:
        books (list[dict]): Extracted books data.
        filename (str): Target CSV filename / path.

    Returns:
        bool: True if saving succeeded, False otherwise.
    """
    if not books:
        print("[!] No book records available to save.")
        return False

    fieldnames = ["title", "price", "star_rating", "availability", "product_url"]

    try:
        with open(filename, mode="w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(books)
        print(f"[+] Successfully wrote {len(books)} records to '{filename}'.")
        return True
    except (IOError, OSError, PermissionError) as file_err:
        print(f"[!] File Write Error: Unable to save to '{filename}': {file_err}")
        return False


def display_summary(books: list[dict]) -> None:
    """
    Prints a formatted summary in the terminal, including total count,
    preview table of the first 5 rows, and the average price.

    Parameters:
        books (list[dict]): The complete list of scraped book dictionaries.
    """
    if not books:
        print("[!] No book data available to display.")
        return

    # Calculate average price
    numeric_prices = []
    for b in books:
        num_str = re.sub(r"[^\d.]", "", b.get("price", ""))
        try:
            numeric_prices.append(float(num_str))
        except ValueError:
            pass

    avg_price = (sum(numeric_prices) / len(numeric_prices)) if numeric_prices else 0.0

    print("\n" + "=" * 90)
    print("                          WEB SCRAPING SUMMARY REPORT")
    print("=" * 90)
    print(f"  Target Website     : https://books.toscrape.com/")
    print(f"  Total Books Scraped: {len(books)}")
    print(f"  Average Book Price : £{avg_price:.2f}")
    print("-" * 90)
    print("  Preview of First 5 Scraped Books:")
    print("-" * 90)
    print(f"  {'#':<3} {'Rating':<8} {'Price':<10} {'Availability':<14} {'Title'}")
    print("  " + "-" * 86)

    for idx, book in enumerate(books[:5], start=1):
        stars_display = f"{book['star_rating']} / 5"
        title_disp = (book['title'][:45] + "...") if len(book['title']) > 48 else book['title']
        print(
            f"  {idx:<3} {stars_display:<8} {book['price']:<10} "
            f"{book['availability']:<14} {title_disp}"
        )

    print("=" * 90 + "\n")


def main() -> None:
    """
    Main orchestration function:
    1. Checks robots.txt permission.
    2. Iterates over pages 1 through 3 of the catalog.
    3. Fetches each page HTML and applies rate limiting (polite sleep).
    4. Parses books from each page.
    5. Saves the combined records to books_data.csv.
    6. Displays terminal summary statistics and a 5-row preview table.
    """
    base_site_url = "https://books.toscrape.com/"
    start_url = "https://books.toscrape.com/catalogue/page-1.html"
    total_pages = 3
    delay_seconds = 1

    print("=" * 70)
    print("    TASK 29: BOOKS TO SCRAPE - WEB SCRAPER (Level 1, Day 29)")
    print("=" * 70)

    # 1. Check robots.txt before making scraping requests
    allowed = check_robots_allowed(start_url, user_agent=DEFAULT_USER_AGENT)
    if not allowed:
        print("[-] Scraping stopped: Prohibited by robots.txt policy.")
        return

    all_books = []

    # 2. Scrape pages 1 through 3
    for page_num in range(1, total_pages + 1):
        page_url = f"https://books.toscrape.com/catalogue/page-{page_num}.html"
        print(f"\n[*] [Page {page_num}/{total_pages}] Fetching: {page_url}")

        html = fetch_page(page_url)
        if html:
            books_on_page = parse_books(html, base_url=page_url)
            all_books.extend(books_on_page)
            print(f"    -> Extracted {len(books_on_page)} books.")
        else:
            print(f"    -> Failed to load content from page {page_num}.")

        # 3. Polite rate-limiting between page requests
        if page_num < total_pages:
            print(f"    -> Sleeping for {delay_seconds} second(s) to be polite...")
            time.sleep(delay_seconds)

    # 4. Save to CSV
    output_filename = DEFAULT_CSV_PATH
    print(f"\n[*] Saving scraped dataset to '{output_filename}'...")
    save_to_csv(all_books, filename=output_filename)

    # 5. Display terminal summary
    display_summary(all_books)


if __name__ == "__main__":
    main()
