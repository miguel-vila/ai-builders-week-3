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

