import requests
from datetime import datetime, timedelta
from xml.etree import ElementTree as ET
import pandas as pd

def parse_date(pubdate_elem):
    year = pubdate_elem.find('Year').text if pubdate_elem.find('Year') is not None else None
    month = pubdate_elem.find('Month').text if pubdate_elem.find('Month') is not None else None
    day = pubdate_elem.find('Day').text if pubdate_elem.find('Day') is not None else None

    if year and month and day:
        try:
            return datetime.strptime(f"{year} {month} {day}", '%Y %b %d').strftime('%Y-%m-%d')
        except ValueError:
            return f"{year}-{month}-{day}"
    elif year:
        return year
    else:
        return "Unbekanntes Datum"

def fetch_details(id_list, api_key):
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    params = {
        'db': 'pubmed',
        'id': ','.join(id_list),
        'retmode': 'xml',
        'api_key': api_key
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        print("Fehler beim Abrufen der Details:", response.status_code)
        return []

    return response.text
    
def parse_article_details(xml_data):
    articles = []
    root = ET.fromstring(xml_data)
    for article in root.findall('.//PubmedArticle'):
        title = article.find('.//ArticleTitle').text
        pubdate_elem = article.find('.//PubDate')
        pubdate = parse_date(pubdate_elem) if pubdate_elem is not None else "Unbekanntes Datum"
        
        abstract_elem = article.find('.//Abstract/AbstractText')
        
        if abstract_elem is not None:
            abstract = abstract_elem.text
            pmid = article.find('.//PMID').text
            link = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
            articles.append({'title': title, 'link': link, 'pubDate': pubdate, 'content': abstract})

    return articles

def search_pubmed(topic, api_key):
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    db = "pubmed"
    end_date = datetime.today().strftime('%Y/%m/%d')
    start_date = (datetime.today() - timedelta(days=1)).strftime('%Y/%m/%d')

    params = {
        'db': db,
        'term': f"{topic}[Title/Abstract]",
        'datetype': 'pdat',
        'mindate': start_date,
        'maxdate': end_date,
        'usehistory': 'n',
        'api_key': api_key,
        'retmode': 'json',
        'retmax': 100
    }

    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        result = response.json()
        id_list = result['esearchresult']['idlist']
        xml_data = fetch_details(id_list, api_key)
        article_details = parse_article_details(xml_data)
        return article_details
    else:
        print(f"Fehler bei der Suche: {response.status_code}")
        return None

def dict_to_dataframe(article_list):
    df = pd.DataFrame.from_records(article_list)
    df.rename(columns={'title': 'title', 'pubdate': 'pubDate', 'abstract': 'content', 'link': 'link'}, inplace=True)
    return df


"""

Für mehrere Topics: Schleife
RateLimit für Pubmed -> Max 10 calls pro sekunde
topic = "COVID-19"
api_key = "deda4be6413bd1ec55b3394d10d12fb47308" 
articles = search_pubmed(topic, api_key)

df = dict_to_dataframe(articles)

display(df)
"""