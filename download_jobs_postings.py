import csv
from jobspy import scrape_jobs

df = scrape_jobs(
    site_name=["indeed", "google"], #, "linkedin", "zip_recruiter", "google"],  # also "glassdoor", "bayt", "naukri", "bdjobs"
    search_term="backend engineer",
    location="usa",            # LinkedIn uses this; Indeed/Glassdoor need country_indeed too
    results_wanted=200,           # per site
    hours_old=24*7*2,                 # last 2 weeks
    country_indeed="usa",    # required for Indeed/Glassdoor country scoping
    linkedin_fetch_description=True,  # slower, fetches full description + direct URL
    # proxies=["user:pass@host:port", "localhost"],  # if you hit rate limits
)

print(len(df), "rows")
df.to_csv("jobs.csv", index=False, quoting=csv.QUOTE_NONNUMERIC)


# import json
# import re
# import time
# from dataclasses import dataclass, asdict
# from typing import List, Optional, Set, Dict
# from urllib.parse import urljoin, urlparse

# import requests
# from bs4 import BeautifulSoup

# BASE = "https://remoteok.com"
# LISTING_BASE = f"{BASE}/remote-dev-jobs"
# HEADERS = {
#     # Use your own descriptive UA; sites often block default ones.
#     "User-Agent": "ResearchBot/0.1 experiments; requests; beautifulsoup4"
# }
# REQUEST_TIMEOUT = 20
# REQUEST_DELAY_SEC = 1.5
# PAGES = 2
# OUTFILE = "jobs_remoteok.jsonl"

# @dataclass
# class Job:
#     url: str
#     title: Optional[str] = None
#     company: Optional[str] = None
#     location: Optional[str] = None
#     tags: Optional[List[str]] = None
#     date: Optional[str] = None  # as text seen on page (e.g., "2d ago")
#     description_text: Optional[str] = None
#     description_html: Optional[str] = None
#     meta: Optional[Dict] = None  # any extra bits we capture defensively


# def get_soup(url: str) -> BeautifulSoup:
#     resp = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
#     resp.raise_for_status()
#     return BeautifulSoup(resp.text, "html.parser")

# def normalize_job_url(href: str) -> Optional[str]:
#     if not href:
#         return None
#     # Accept absolute or relative; filter to RemoteOK job detail pages
#     abs_url = urljoin(BASE, href)
#     parsed = urlparse(abs_url)
#     if parsed.netloc not in ("remoteok.com", "www.remoteok.com"):
#         return None
#     # Heuristic: job detail URLs typically contain "/remote-jobs/"
#     if "/remote-jobs/" in parsed.path:
#         return abs_url.split("?")[0]
#     return None


# def extract_job_links_from_listing(soup: BeautifulSoup) -> List[str]:
#     """Collect job detail links from a listing page."""
#     links: Set[str] = set()

#     # def is_link(tag):
#     #     return tag.

#     # Strategy 1: any anchor whose href matches /remote-jobs/
#     for a in soup.find_all(name ='a', href=True):
#         print(f"[job] Found job link: {a['href']}")
#         # print(f"[job] Found job link: {a['href']}")
#         url = normalize_job_url(a["href"])
#         if url:
#             links.add(url)

#     # Strategy 2: some cards may have data-href attributes (defensive)
#     for tag in soup.find_all(attrs={"data-href": True}):
#         url = normalize_job_url(tag.get("data-href"))
#         if url:
#             links.add(url)

#     # Strategy 3: look for job rows/cards container patterns and pull anchors
#     # (optional, often covered by Strategy 1)
#     return sorted(links)


# def text_or_none(el) -> Optional[str]:
#     return el.get_text(strip=True) if el else None


# def extract_text_list(els) -> List[str]:
#     out = []
#     for el in els or []:
#         t = el.get_text(strip=True)
#         if t:
#             out.append(t)
#     # de-dup while preserving order
#     seen = set()
#     uniq = []
#     for t in out:
#         if t not in seen:
#             uniq.append(t)
#             seen.add(t)
#     return uniq


# def fetch_job_detail(url: str) -> Job:
#     soup = get_soup(url)

#     # Try multiple selector strategies to reduce brittleness:
#     title = None
#     company = None
#     location = None
#     date = None
#     tags: List[str] = []
#     meta: Dict[str, str] = {}

#     # Title candidates
#     title_candidates = [
#         ("h1", {}),
#         ("h2", {"class": re.compile(r"(title|posting|job|position)", re.I)}),
#         ("meta", {"property": "og:title"}),  # content attribute
#     ]
#     for tag, attrs in title_candidates:
#         el = soup.find(tag, attrs=attrs)
#         if el:
#             if tag == "meta":
#                 title = el.get("content")
#             else:
#                 title = text_or_none(el)
#         if title:
#             break

#     # Company candidates
#     company_candidates = [
#         ("div", {"class": re.compile(r"(company|employer)", re.I)}),
#         ("span", {"class": re.compile(r"(company|employer)", re.I)}),
#         ("a", {"class": re.compile(r"(company|employer)", re.I)}),
#         ("meta", {"property": "og:site_name"}),
#     ]
#     for tag, attrs in company_candidates:
#         el = soup.find(tag, attrs=attrs)
#         if el:
#             if tag == "meta":
#                 company = el.get("content")
#             else:
#                 txt = text_or_none(el)
#                 # Avoid a generic "Remote OK" fallback if found in og:site_name
#                 if txt and txt.lower() not in ("remote ok", "remoteok"):
#                     company = txt
#             if company:
#                 break

#     # Location candidates
#     loc_candidates = [
#         ("div", {"class": re.compile(r"(location|region)", re.I)}),
#         ("span", {"class": re.compile(r"(location|region)", re.I)}),
#         ("p", {"class": re.compile(r"(location|region)", re.I)}),
#     ]
#     for tag, attrs in loc_candidates:
#         el = soup.find(tag, attrs=attrs)
#         if el:
#             location = text_or_none(el)
#             if location:
#                 break

#     # Date/posted time candidates
#     date_candidates = [
#         ("time", {}),
#         ("span", {"class": re.compile(r"(date|posted|ago|time)", re.I)}),
#         ("div", {"class": re.compile(r"(date|posted|ago|time)", re.I)}),
#     ]
#     for tag, attrs in date_candidates:
#         el = soup.find(tag, attrs=attrs)
#         if el:
#             date = text_or_none(el)
#             if date:
#                 break

#     # Tags/skills candidates
#     tag_wrappers = soup.find_all(["a", "span", "div"], class_=re.compile(r"(tag|skill|keyword)", re.I))
#     tags = extract_text_list(tag_wrappers)

#     # Description: try a few common containers, fallback to main content
#     desc_candidates = [
#         ("div", {"id": re.compile(r"(description|job-description)", re.I)}),
#         ("section", {"id": re.compile(r"(description|job-description|job)", re.I)}),
#         ("div", {"class": re.compile(r"(description|content|markdown|prose)", re.I)}),
#         ("article", {}),
#         ("main", {}),
#     ]

#     description_html = None
#     description_text = None
#     for tag, attrs in desc_candidates:
#         el = soup.find(tag, attrs=attrs)
#         if el and el.get_text(strip=True):
#             description_html = str(el)
#             description_text = el.get_text("\n", strip=True)
#             break

#     # Fallback to body text if nothing else
#     if not description_text:
#         body = soup.find("body")
#         if body:
#             description_html = str(body)
#             description_text = body.get_text("\n", strip=True)

#     # Capture extras (meta og: tags) for debugging/use
#     for prop in ["og:title", "og:description", "og:url"]:
#         m = soup.find("meta", {"property": prop})
#         if m and m.get("content"):
#             meta[prop] = m["content"]

#     return Job(
#         url=url,
#         title=title,
#         company=company,
#         location=location,
#         tags=tags or None,
#         date=date,
#         description_text=description_text,
#         description_html=description_html,
#         meta=meta or None,
#     )


# def scrape_pages(pages: int = PAGES) -> List[Job]:
#     all_job_urls: List[str] = []
#     for p in range(1, pages + 1):
#         page_url = LISTING_BASE if p == 1 else f"{LISTING_BASE}?p={p}"
#         print(f"[list] Fetching {page_url}")
#         soup = get_soup(page_url)
#         links = extract_job_links_from_listing(soup)
#         print(f"[list] Found {len(links)} candidate job URLs on page {p}")
#         all_job_urls.extend(links)
#         time.sleep(REQUEST_DELAY_SEC)

#     # De-dup while preserving order
#     seen: Set[str] = set()
#     unique_urls: List[str] = []
#     for u in all_job_urls:
#         if u not in seen:
#             unique_urls.append(u)
#             seen.add(u)

#     print(f"[list] Total unique job URLs from {pages} pages: {len(unique_urls)}")

#     jobs: List[Job] = []
#     # for i, url in enumerate(unique_urls, 1):
#     #     try:
#     #         print(f"[job] ({i}/{len(unique_urls)}) Fetching {url}")
#     #         job = fetch_job_detail(url)
#     #         jobs.append(job)
#     #     except requests.HTTPError as e:
#     #         print(f"[job] HTTP error for {url}: {e}")
#     #     except Exception as e:
#     #         print(f"[job] Error for {url}: {e}")
#     #     time.sleep(REQUEST_DELAY_SEC)
#     return jobs


# def save_jsonl(jobs: List[Job], filename: str = OUTFILE) -> None:
#     with open(filename, "w", encoding="utf-8") as f:
#         for job in jobs:
#             f.write(json.dumps(asdict(job), ensure_ascii=False) + "\n")
#     print(f"[out] Wrote {len(jobs)} jobs to {filename}")

# if __name__ == "__main__":
#     jobs = scrape_pages(pages=2)
#     save_jsonl(jobs)
