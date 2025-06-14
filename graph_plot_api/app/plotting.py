from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import StreamingResponse
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import mplfinance as mpf
import io
import os
import matplotlib.font_manager as fm

font_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "fonts", "ipaexg.ttf")
)
jp_font = fm.FontProperties(fname=font_path)
plt.rcParams['font.family'] = jp_font.get_name()

# デバッグ用に確認！
print("指定フォント名:", jp_font.get_name())
print("matplotlibが実際に使ってるフォント:", plt.rcParams['font.family'])


from app.utils import (
    calc_rsi, calc_bb, calc_macd, calc_sma, calc_ema
)

router = APIRouter()

# 対応しているテクニカル指標
VALID_INDICATORS = {
    "RSI": calc_rsi,
    "BBANDS": calc_bb,
    "MACD": calc_macd,
    "SMA": calc_sma,
    "EMA": calc_ema
}

@router.get("/plot")
def plot_chart(
    ticker: str,
    period: str = "1y",
    indicators: list[str] = Query(default=[]),
    graphType: str = "line"
):
    if len(indicators) > 3:
        raise HTTPException(400, detail="テクニカル指標は最大3つまでです。")

    if graphType not in ["line", "candle"]:
        raise HTTPException(400, detail="graphTypeは'line'または'candle'のいずれかです。")

    # 株価データ取得
    df = yf.download(ticker, period=period, group_by="column")
    if df.empty:
        raise HTTPException(404, detail="指定された銘柄コードではデータが取得できませんでした。")

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.droplevel(1)


    fig, (ax1, ax2) = plt.subplots(
    2, 1, figsize=(12, 8), sharex=True,
    gridspec_kw={'height_ratios': [3, 1]}
    )

    

    # メインチャート：終値の線 or ローソク足
    if graphType == "line":
        ax1.plot(df.index, df["Close"], label="終値", color="blue")
        ax1.set_title(f"{ticker} 株価チャート",fontproperties=jp_font)
    elif graphType == "candle":
        df_candle = df[["Open", "High", "Low", "Close", "Volume"]].copy()
        df_candle = df_candle.dropna()
        df_candle = df_candle.astype("float64")
   
        df_candle.index.name = "Date"

        s = mpf.make_mpf_style(base_mpf_style='yahoo', rc={'font.family': jp_font.get_name()})


        fig_mpf, axes = mpf.plot(
            df_candle,
            type='candle',
            style=s,
            volume=True,
            returnfig=True,
            figratio=(16, 9),
            figscale=1.2,
            panel_ratios=(3, 1)
        )

        axes[0].set_title(f"{ticker} 株価チャート", fontproperties=jp_font)
        axes[0].set_ylabel("価格", fontproperties=jp_font)
        axes[2].set_ylabel("出来高", fontproperties=jp_font)

        buf = io.BytesIO()
        fig_mpf.savefig(buf, format="png")
        buf.seek(0)
        plt.close(fig_mpf)

        return StreamingResponse(buf, media_type="image/png")
    
    # テクニカル指標を追加
    for indicator in indicators:
        if indicator not in VALID_INDICATORS:
            continue

        func = VALID_INDICATORS[indicator]

        if indicator == "BBANDS":
            upper, middle, lower = func(df["Close"])
            ax1.fill_between(df.index, lower, upper, color="gray", alpha=0.2, label="ボリンジャーバンド")
            ax1.plot(df.index, middle, label="BB 中央線", color="gray", linestyle=":")

        elif indicator == "MACD":
            macd, signal, hist = func(df["Close"])
            hist = pd.Series(hist).squeeze()
            if len(hist.shape) > 1:
                hist = hist.squeeze(axis=1)
            ax2.plot(df.index, macd, label="MACD", color="purple")
            ax2.plot(df.index, signal, label="Signal", color="orange")
            ax2.fill_between(df.index, hist, 0, alpha=0.3, label="Hist")

        elif indicator == "RSI":
            rsi = func(df["Close"])
            ax2.plot(df.index, rsi, label="RSI", color="green")
            ax2.axhline(70, color="red", linestyle="--", linewidth=1)
            ax2.axhline(30, color="red", linestyle="--", linewidth=1)
            ax2.set_ylim(0, 100)  
            ax2.set_ylabel("RSI")

        elif indicator == "SMA":
            for window in [5, 25, 75]:
                sma = df["Close"].rolling(window=window).mean()
                ax1.plot(df.index, sma, label=f"SMA{window}")

        elif indicator == "EMA":
            for span in [5, 25, 75]:
                ema = df["Close"].ewm(span=span, adjust=False).mean()
                ax1.plot(df.index, ema, label=f"EMA{span}")

        else:
            values = func(df["Close"])
            ax1.plot(df.index, values, label=indicator)

    if not any(i in indicators for i in ["RSI", "MACD"]):
        fig.delaxes(ax2)
        ax1.tick_params(labelbottom=True)
        ax1.set_xlabel("日付",fontproperties=jp_font)
        ax1.tick_params(axis="x", labelrotation=45)

    fig.tight_layout()

    ax1.legend(prop=jp_font)
    buf = io.BytesIO()
    plt.savefig(buf, format="png",bbox_inches="tight")
    buf.seek(0)
    plt.close(fig)

    return StreamingResponse(buf, media_type="image/png")
