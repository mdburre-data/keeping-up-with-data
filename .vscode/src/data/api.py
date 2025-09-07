# api.py
from fastapi import FastAPI, HTTPException
from trend_predictor import fetch_trends, train_prophet_and_predict
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

@app.get("/predict")
async def predict(keyword: str, periods: int = 12):
    try:
        df = fetch_trends(keyword)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    preds = train_prophet_and_predict(df, periods=periods)
    return {"keyword": keyword, "predictions": preds.to_dict(orient='records')}
