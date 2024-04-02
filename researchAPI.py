import requests
from datetime import datetime, timedelta
import pandas as pd
import feedparser
import time



# Call Crossref API
def search_crossref(keyword, timeSince):
    today = datetime.now()
    yesterday = today - timedelta(days=timeSince)
    date_filter = yesterday.strftime("%Y-%m-%d")

    # Crossref URL for API call
    url = f"https://api.crossref.org/works?query={keyword}&filter=from-pub-date:{date_filter},until-pub-date:{today.strftime('%Y-%m-%d')},has-abstract:true"
    
    response = requests.get(url)
    data = response.json()
    
    crossref_results = []
    
    for item in data.get('message', {}).get('items', []):
        title = item.get('title', [''])[0]
        date = item.get('created', {}).get('date-time', '')
        abstract = item.get('abstract', '')
        doi = item.get('DOI', '')
        link = f"https://doi.org/{doi}"
        
        crossref_results.append({"title": title, "link": link, "pubDate": date, "content": abstract})
        
    return crossref_results

# Arxiv call
def search_arxiv(keyword, timeSince):
    start_date = (datetime.now() - timedelta(days=timeSince)).strftime("%Y%m%d")
    end_date = datetime.now().strftime("%Y%m%d")

    base_url = 'http://export.arxiv.org/api/query?'
    query = f"search_query=all:{keyword}+AND+submittedDate:[{start_date}+TO+{end_date}]&sortBy=submittedDate&sortOrder=descending&max_results=10"
    url = base_url + query
    
    response = requests.get(url)
    feed = feedparser.parse(response.content)
    
    arxiv_results = []
    
    for entry in feed.entries:
        title = entry.title
        date = entry.published
        summary = entry.summary
        link = entry.link
        
        arxiv_results.append({"title": title, "link": link, "pubDate": date, "content": summary})
        
    return arxiv_results

def search_research_papers(keywords, timeSince):
    combined_results = []

    # Iteriere über jedes Keyword
    for keyword in keywords:
        crossref_results = search_crossref(keyword, timeSince)
        arxiv_results = search_arxiv(keyword, timeSince)
        combined_results += crossref_results + arxiv_results

        # 3 Sekunden Limit wegen arxiv
        time.sleep(3)

    # Definiere die Spalten für den DataFrame
    columns = ["title", "link", "pubDate", "content"]

    # Erstelle einen DataFrame mit den kombinierten Ergebnissen
    df = pd.DataFrame(combined_results, columns=columns)
    
    return df


# Example Call
# 10 -> Heute - 10 Tage
# df2 = search_research_papers(["ChatGPT", "Bitcoin", "Cryptocurrency"], 10)
