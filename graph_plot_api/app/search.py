from fastapi import APIRouter, Query
import pandas as pd
import os

router = APIRouter()

# codes.csv のパスを取得
CSV_PATH = os.path.join(os.path.dirname(__file__), "codes.csv")

# CSVファイルを読み込んでメモリに保持（1回だけ）
try:
    df_codes = pd.read_csv(CSV_PATH, dtype={"code": str, "name": str})
    df_codes.columns = [col.strip().replace("　", "").replace(" ", "") for col in df_codes.columns]
    df_codes = df_codes.rename(columns={"銘柄名": "name", "銘柄コード": "code"})
except Exception as e:
    raise RuntimeError(f"銘柄コードファイルの読み込みに失敗しました: {e}")

@router.get("/search_suggestions")
def search_suggestions(q: str = Query(..., min_length=1, description="銘柄名の部分一致検索ワード")):
    """
    銘柄名に部分一致する候補を最大10件返す
    """
    matched = df_codes[
        df_codes["name"].str.contains(q, case=False, na=False)
    ]
    results = matched.head(10)[["code", "name"]].to_dict(orient="records")
    return results