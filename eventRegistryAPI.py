# Event registry
# Key 68c9166c-b4d5-47e1-8607-a8d9447808f9
from eventregistry import *
from datetime import datetime, timedelta
import pandas as pd

def get_News_EventRegistry(keywords):
    er = EventRegistry(apiKey = "68c9166c-b4d5-47e1-8607-a8d9447808f9")
    
    now = datetime.now()

    columns = ["title", "link", "pubDate", "content"]
    df = pd.DataFrame(columns=columns)
    
    # Ein Tag zurück
    date_start = now - timedelta(days=1)
    date_start_formatted = date_start.strftime("%Y-%m-%d")

    
    # get the USA URI
    #usUri = er.getLocationUri("USA")    # = http://en.wikipedia.org/wiki/United_States
    #gerUri = "http://en.wikipedia.org/wiki/Germany"
    
    q = QueryArticlesIter(
        keywords = QueryItems.OR(keywords),
        dataType = ["news", "blog"],
        dateStart=date_start_formatted,
        isDuplicateFilter="skipDuplicates",
        lang=["eng", "deu"])
    
    columns = ["Title", "Date", "Text", "Link"]
    df = pd.DataFrame(columns=columns)
    
    # obtain at most 500 newest articles or blog posts, remove maxItems to get all
    for art in q.execQuery(er, sortBy = "date", maxItems = 200):
        df = pd.concat([df, pd.DataFrame({"Title": [art["title"]], "Date": [art["date"]], "Text": [art["body"]], "Link": [art["url"]]})], ignore_index=True)

    return df

"""
df = get_News_EventRegistry(["Ai Agent", "MemGPT"])
"""