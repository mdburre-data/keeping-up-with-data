# trend_predictor.py
from pytrends.request import TrendReq
import pandas as pd
from prophet import Prophet
import json
from datetime import datetime

def fetch_trends(keyword, timeframe='today 5-y', geo='US'):
    pytrends = TrendReq(hl='en-US', tz=360)
    pytrends.build_payload([keyword], cat=0, timeframe=timeframe, geo=geo, gprop='')
    df = pytrends.interest_over_time()
    if df.empty:
        raise ValueError("No data returned for keyword: "+keyword)
    df = df.reset_index()[['date', keyword]]
    df.columns = ['ds', 'y']
    # Prophet expects ds (datetime) and y (numeric)
    return df

def train_prophet_and_predict(df, periods=12, freq='W'):
    m = Prophet()  # tune seasonality if needed
    m.fit(df)
    future = m.make_future_dataframe(periods=periods, freq=freq)
    forecast = m.predict(future)
    # return only ds and yhat, yhat_lower, yhat_upper
    out = forecast[['ds','yhat','yhat_lower','yhat_upper']].tail(periods)
    return out

if __name__ == "__main__":
    kw = "oversized blazer"   # example — loop over your keyword list in practice
    df = fetch_trends(kw, timeframe='today 5-y', geo='US')
    preds = train_prophet_and_predict(df, periods=12, freq='W')
    result = {
        "keyword": kw,
        "predictions": preds.to_dict(orient='records'),
        "last_observed": df.tail(1).to_dict(orient='records')[0]
    }
    print(json.dumps(result, default=str, indent=2))
