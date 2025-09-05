from fastapi import FastAPI
from fetch_trends import fetch_interest, fetch_rising
from cluster import cluster_terms
from scoring import momentum_score
import pandas as pd
from prophet import Prophet
import openai, os, json # type: ignore

openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI(title="Fashion Trend Radar")
DATA = {}

# Load category seeds
with open("categories.json") as f:
    CATEGORIES = json.load(f)

@app.post("/ingest")
def ingest():
    """
    Pull Google Trends for all categories
    """
    all_terms = [t for group in CATEGORIES.values() for t in group]
    df = fetch_interest(all_terms)
    DATA["trends"] = df
    return {"status": "ok", "terms": len(all_terms)}

@app.get("/trends/top")
def top_trends(limit: int = 20):
    if "trends" not in DATA:
        return {"error": "No data"}

    df = DATA["trends"]
    results = []

    for term in [c for c in df.columns if c != "date"]:
        ts = df[["date", term]].dropna()
        if ts.empty:
            continue

        score, label = momentum_score(ts[term])

        # AI summary
        try:
            summary = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[
                    {"role":"system","content":"You are a fashion trend analyst."},
                    {"role":"user","content":f"Explain why '{term}' is trending in fashion in 2 sentences."}
                ]
            )["choices"][0]["message"]["content"]
        except Exception:
            summary = f"{term} is trending in fashion searches."

        # Detect category
        cat = next((k for k,v in CATEGORIES.items() if term in v), "other")

        results.append({
            "concept": term,
            "category": cat,
            "score": score,
            "label": label,
            "summary": summary
        })

    # Sort by score
    out = sorted(results, key=lambda x: x["score"], reverse=True)[:limit]
    return out

@app.get("/trends/{concept}")
def trend_detail(concept: str):
    if "trends" not in DATA or concept not in DATA["trends"].columns:
        return {"error": "Not found"}
    df = DATA["trends"][["date", concept]].rename(columns={concept:"y"})
    df = df.rename(columns={"date":"ds"})

    m = Prophet()
    m.fit(df)
    future = m.make_future_dataframe(periods=8, freq="W")
    fc = m.predict(future)

    return {
        "history": df.tail(26).to_dict(orient="records"),
        "forecast": fc.tail(8)[["ds","yhat","yhat_lower","yhat_upper"]].to_dict(orient="records")
    }

@app.post("/trends/cluster")
def cluster_trends():
    """
    Cluster rising Google queries into themes
    """
    seeds = [t for g in CATEGORIES.values() for t in g]
    rising = fetch_rising(seeds)
    if rising.empty:
        return {"clusters": []}

    queries = rising["query"].unique().tolist()
    clusters = cluster_terms(queries)
    return {"clusters": clusters}
