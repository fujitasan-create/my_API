from fastapi import APIRouter, Query, HTTPException
import yfinance as yf

router = APIRouter()

def format_market_cap(value):
    if value is None:
        return "未定"
    elif value >= 1e12:
        return f"{round(value / 1e12, 2)} 兆円"
    elif value >= 1e8:
        return f"{round(value / 1e8, 2)} 億円"
    else:
        return f"{value} 円"

def interpret_per(per):
    if per is None:
        return "未定"
    elif per > 40:
        return f"{per} 倍（割高の可能性あり）"
    elif per < 10:
        return f"{per} 倍（割安の可能性あり）"
    else:
        return f"{per} 倍"

def safe(value):
    return "未定" if value is None else value

@router.get("/info")
def get_stock_info(ticker: str = Query(..., description="ティッカーコード")):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        return {
            "現在の株価": safe(info.get("currentPrice")),
            "日中の値動き": f"{safe(info.get('dayLow'))}円 〜 {safe(info.get('dayHigh'))}円",
            "52週の変動幅": f"{safe(info.get('fiftyTwoWeekLow'))}円 〜 {safe(info.get('fiftyTwoWeekHigh'))}円",
            "平均出来高": f"{round(info.get('averageVolume')/1e6,2)} 百万株" if info.get("averageVolume") else "未定",
            "時価総額": format_market_cap(info.get("marketCap")),
            "EPS（1株あたり利益）": safe(info.get("trailingEps")),
            "PER（株価収益率）": interpret_per(info.get("trailingPE")),
            "配当利回り": f"{round(info.get('dividendYield')*100,2)} %" if info.get("dividendYield") else "未定"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
