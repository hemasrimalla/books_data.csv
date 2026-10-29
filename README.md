# Web Scraper — Books to Scrape (Level 1, Day 29)

A modular, robust, and ethical Python web scraper built for **Task 29: Create a Web Scraping Program**. This project extracts publicly available book catalog data from [Books to Scrape](https://books.toscrape.com/) (an educational sandbox for web scraping) across multiple catalog pages, performs data parsing and conversion, and stores the results in a clean UTF-8 encoded CSV file.

---

## 🎯 Learning Objectives & Project Goals

- **HTTP Communication**: Understand how to formulate polite HTTP GET requests with custom User-Agent headers, timeouts, and exception handling using `requests`.
- **HTML Parsing & DOM Traversal**: Inspect HTML element structures and extract attributes, textual data, and CSS class-based values using `BeautifulSoup4` (`bs4`).
- **Ethical Web Scraping**: Check and honor `robots.txt` using Python's standard library `urllib.robotparser`, implement polite request delays (`time.sleep`), and handle missing elements gracefully.
- **Data Persistence**: Export structured tabular data into standard CSV format with headers using Python's built-in `csv` module.
- **Summary & Insights**: Calculate and output terminal statistics, including total records scraped, average price, and sample preview tables.

---

## 📚 Answers to Core Concepts

### 1. What is Web Scraping?
**Web scraping** is an automated technique used to extract data from websites. Instead of manually copying and pasting information from a browser, a scraper sends automated HTTP requests to fetch web pages (HTML, JSON, or XML) and parses the page source code to extract structured data (such as product titles, prices, ratings, and URLs) for analysis, indexing, or storage.

### 2. Is Web Scraping Legal and Ethical?
**Yes, but with crucial conditions and responsibilities:**
- **Public Data**: Scraping publicly accessible data that is not behind authentication or paywalls is generally considered legal (as affirmed in landmark cases such as *hiQ Labs v. LinkedIn*).
- **Robots.txt & Terms of Service (ToS)**: Always check `robots.txt` and review the website's Terms of Service. If a site explicitly prohibits scraping in its terms or disallows specific user paths, scraping those paths violates site rules.
- **Copyright & Sensitive Data**: Scraping copyrighted content, proprietary intellectual property, or personal private data (PII) may breach copyright laws, GDPR, CCPA, or regional privacy regulations.
- **Server Load (Politeness)**: Unthrottled scrapers can flood servers with requests, creating a Denial of Service (DoS) impact. Scrapers must implement rate-limiting, backoffs, and descriptive User-Agent headers.

### 3. What is the Difference Between `requests` and `BeautifulSoup`?
| Feature / Role | `requests` | `BeautifulSoup` (`bs4`) |
| :--- | :--- | :--- |
| **Primary Purpose** | HTTP Client (Network layer) | HTML/XML Parser (Document layer) |
| **What it does** | Sends HTTP requests (GET, POST, etc.) across the network and downloads raw HTML/text responses from web servers. | Parses raw HTML strings into a navigable Python Document Object Model (DOM) tree. |
| **What it cannot do** | Cannot search, filter, or parse HTML tags, CSS classes, or attributes. | Cannot make network calls or download web pages over the internet by itself. |
| **How they collaborate** | `requests` fetches the webpage source code: `response.text`. | `BeautifulSoup` takes `response.text` and extracts target tags: `soup.find_all("article")`. |

---

## 🛡️ Ethical Scraping Best Practices

This project implements standard web scraping etiquette:

1. **`robots.txt` Compliance**: Prior to initiating data extraction, the scraper verifies `https://books.toscrape.com/robots.txt` via `urllib.robotparser.RobotFileParser`. It proceeds only if fetching the target catalogue path is permitted.
2. **Descriptive User-Agent**: The scraper advertises its identity, purpose, and contact URL in the HTTP request headers (`BookScraperBot/1.0 (+https://github.com/hemasrimalla/web-scraper)`), avoiding anonymous or misleading bot behavior.
3. **Polite Rate Limiting**: Adds a deliberate pause (`time.sleep(1)`) between successive page requests to prevent server strain or spike traffic.
4. **Timeouts & Exception Handling**: Includes a 10-second network timeout and defensive try/except handling for timeouts, network drops, HTTP status codes, and missing HTML nodes.

---

## 📋 Explanation of Extracted Fields

The scraper targets `<article class="product_pod">` on each catalog page and extracts the following 5 structured attributes:

| Field Name | Data Type | HTML Tag & Selector | Explanation & Extraction Method |
| :--- | :--- | :--- | :--- |
| **`title`** | `String` | `<h3><a title="...">` | Full book title. Extracted from the `title` attribute of the anchor tag inside `<h3>` because visible anchor text is truncated with ellipses (`...`). |
| **`price`** | `String` | `<p class="price_color">` | The retail price with currency symbol (e.g., `£51.77`). Extracted via `.get_text(strip=True)` and cleaned of encoding artifacts. |
| **`star_rating`** | `Integer` (`1`–`5`) | `<p class="star-rating <Word>">` | Star rating mapped from CSS classes (`One` $\to$ `1`, `Two` $\to$ `2`, `Three` $\to$ `3`, `Four` $\to$ `4`, `Five` $\to$ `5`). |
| **`availability`** | `String` | `<p class="instock availability">` | Stock status (e.g., `"In stock"`). Extracted from `.get_text(strip=True)` while stripping excessive whitespace and child icon tags. |
| **`product_url`** | `String` | `<h3><a href="...">` | Full absolute URL to the product's individual detail page. Formed by resolving relative `href` links using `urllib.parse.urljoin(base_url, href)`. |

---

## 📊 Sample CSV Output (`books_data.csv`)

```csv
title,price,star_rating,availability,product_url
A Light in the Attic,£51.77,3,In stock,https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html
Tipping the Velvet,£53.74,1,In stock,https://books.toscrape.com/catalogue/tipping-the-velvet_999/index.html
Soumission,£50.10,1,In stock,https://books.toscrape.com/catalogue/soumission_998/index.html
Sharp Objects,£47.82,4,In stock,https://books.toscrape.com/catalogue/sharp-objects_997/index.html
Sapiens: A Brief History of Humankind,£54.23,5,In stock,https://books.toscrape.com/catalogue/sapiens-a-brief-history-of-humankind_996/index.html
```

---

## 🚀 Installation & Usage

### 1. Clone the Repository
```bash
git clone https://github.com/hemasrimalla/web-scraper.git
cd web-scraper
```

### 2. Create and Activate a Virtual Environment
- **On Windows (PowerShell):**
  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  ```
- **On Linux / macOS:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Scraper
```bash
python scraper.py
```

### 5. Terminal Output Preview
```text
======================================================================
    TASK 29: BOOKS TO SCRAPE - WEB SCRAPER (Level 1, Day 29)
======================================================================
[*] Checking robots.txt at: https://books.toscrape.com/robots.txt
[+] robots.txt allows access to 'https://books.toscrape.com/catalogue/page-1.html' for User-Agent: 'BookScraperBot/1.0 (+https://github.com/hemasrimalla/web-scraper; educational practice)'.

[*] [Page 1/3] Fetching: https://books.toscrape.com/catalogue/page-1.html
    -> Extracted 20 books.
    -> Sleeping for 1 second(s) to be polite...

[*] [Page 2/3] Fetching: https://books.toscrape.com/catalogue/page-2.html
    -> Extracted 20 books.
    -> Sleeping for 1 second(s) to be polite...

[*] [Page 3/3] Fetching: https://books.toscrape.com/catalogue/page-3.html
    -> Extracted 20 books.

[*] Saving scraped dataset to 'books_data.csv'...
[+] Successfully wrote 60 records to 'books_data.csv'.

==========================================================================================
                          WEB SCRAPING SUMMARY REPORT
==========================================================================================
  Target Website     : https://books.toscrape.com/
  Total Books Scraped: 60
  Average Book Price : £34.84
------------------------------------------------------------------------------------------
  Preview of First 5 Scraped Books:
------------------------------------------------------------------------------------------
  #   Rating   Price      Availability   Title
  --------------------------------------------------------------------------------------
  1   3 / 5    £51.77     In stock       A Light in the Attic
  2   1 / 5    £53.74     In stock       Tipping the Velvet
  3   1 / 5    £50.10     In stock       Soumission
  4   4 / 5    £47.82     In stock       Sharp Objects
  5   5 / 5    £54.23     In stock       Sapiens: A Brief History of Humankind
==========================================================================================
```

---

## 📂 Project Structure

```
web-scraper/
│
├── scraper.py           # Main scraping script with modular functions
├── books_data.csv       # Extracted dataset (60 books across pages 1 to 3)
├── requirements.txt     # Python dependencies (requests, beautifulsoup4)
├── .gitignore           # Ignores venv, pycache, and OS files
└── README.md            # Comprehensive documentation & educational guide
```

---

## 🛠️ Tech Stack & Dependencies
- **Language**: Python 3
- **Networking**: `requests`
- **Parsing**: `beautifulsoup4`
- **Standard Libraries**: `csv`, `urllib.robotparser`, `urllib.parse`, `time`, `re`

---

## 👩‍💻 Author
**Hemasri Malla**  
GitHub: [@hemasrimalla](https://github.com/hemasrimalla)
