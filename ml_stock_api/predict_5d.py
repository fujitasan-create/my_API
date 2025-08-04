from fastapi import APIRouter, HTTPException, Query
import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from imblearn.over_sampling import SMOTE
from sklearn.metrics import classification_report

# talibは使わず、utilsから関数を使う
from graph_plot_api.app.utils import calc_rsi, calc_macd, calc_sma, calc_ema, calc_bb

router = APIRouter()

@router.get("/predict-5d")
def predict_stock_5d(
    ticker: str = Query(..., description="銘柄コード（例：AAPL）"),
    threshold: float = Query(0.25, ge=0.0, le=1.0, description="予測のしきい値（0〜1）")
):
    try:
        df = yf.download(ticker, period="5y")
        if df.empty:
            raise HTTPException(status_code=404, detail="株価データが見つかりません")

        # 5営業日後の終値と現在を比較してラベル化
        df["target"] = ((df["Close"].shift(-5) / df["Close"]) > 1.01).astype(int)

        # テクニカル指標（utils.py）
        df["RSI"] = calc_rsi(df["Close"])
        df["macd"], df["macdsignal"], df["macdhist"] = calc_macd(df["Close"])
        df["sma5"] = calc_sma(df["Close"], 5)
        df["sma25"] = calc_sma(df["Close"], 25)
        df["ema12"] = calc_ema(df["Close"], 12)
        df["upper"], _, df["lower"] = calc_bb(df["Close"])
        df["BTY"] = df["High"] - df["Low"]
        df["smax"] = df["sma5"] - df["sma25"]

        # 特徴量と目的変数
        X = df[["Open", "Close", "BTY", "smax", "sma5", "sma25", "ema12",
                "macd", "macdsignal", "macdhist", "RSI", "upper", "lower", "Volume"]]
        y = df["target"]

        df_model = pd.concat([X, y], axis=1).dropna()
        if len(df_model) < 100:
            raise HTTPException(status_code=422, detail="学習に十分なデータがありません")

        X = df_model[X.columns]
        y = df_model["target"]

        # 前処理・SMOTE
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=0)
        smote = SMOTE(random_state=0)
        X_train_resampled, y_train_resampled = smote.fit_resample(X_train, y_train)

        # モデル学習
        model = GradientBoostingClassifier(max_depth=5, n_estimators=200, subsample=0.8, learning_rate=0.10)
        model.fit(X_train_resampled, y_train_resampled)

        # 推論
        proba = model.predict_proba(X_test)[:, 1]
        pred = (proba >= threshold).astype(int)

        # 最新の1件を返す
        latest_proba = proba[-1]
        latest_pred = pred[-1]
        direction = "上がる" if latest_pred == 1 else "下がる"

        return {
            "ticker": ticker,
            "prediction": direction,
            "probability": round(float(latest_proba), 3),
            "target_period": "5営業日後"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))