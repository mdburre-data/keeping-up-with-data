from pytrends.request import TrendReq
import pandas as pd

pytrends = TrendReq(hl='en-US', tz=0)

def fetch_interest(terms, timeframe="today 12-m", geo="US"):
    pytrends.build_payload(terms, cat=18, timeframe=timeframe, geo=geo)
    df = pytrends.interest_over_time().reset_index()
    return df.drop(columns=["isPartial"], errors="ignore")

def fetch_rising(seed_terms, timeframe="today 3-m", geo="US"):
    pytrends.build_payload(seed_terms, cat=18, timeframe=timeframe, geo=geo)
    related = pytrends.related_queries()
    out = []
    for term, d in related.items():
        if d and d.get("rising") is not None:
            rising = d["rising"][["query","value"]]
            rising["seed"] = term
            out.append(rising)
    return pd.concat(out, ignore_index=True) if out else pd.DataFrame()
