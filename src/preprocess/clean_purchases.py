"""Open E-commerce 1.0 구매 데이터 기본 정제.

입력: data/raw/open_ecommerce/amazon-purchases.csv (Harvard Dataverse 원본)
출력:
  data/interim/cleaned_purchase/purchases.parquet  정제된 구매 테이블
  data/interim/cleaned_purchase/asin_list.csv      ASIN별 구매 건수

실행: python -m src.preprocess.clean_purchases
"""
import argparse
import re
from pathlib import Path

import pandas as pd

RAW = Path("data/raw/open_ecommerce/amazon-purchases.csv")
OUT_DIR = Path("data/interim/cleaned_purchase")

# 원본 컬럼명 -> 팀 통일 컬럼명
RENAME = {
    "Order Date": "order_date",
    "Purchase Price Per Unit": "unit_price",
    "Quantity": "quantity",
    "Shipping Address State": "state",
    "Title": "title",
    "ASIN/ISBN (Product Code)": "asin",
    "Category": "category",
    "Survey ResponseID": "response_id",
}

ASIN_RE = re.compile(r"^B0[0-9A-Z]{8}$")   # 일반 상품 ASIN
ISBN10_RE = re.compile(r"^[0-9]{9}[0-9X]$")  # 도서는 ISBN-10이 ASIN 자리에 들어감


def classify_code(code) -> str:
    if pd.isna(code) or str(code).strip() == "":
        return "missing"
    code = str(code).strip().upper()
    if ASIN_RE.match(code):
        return "asin"
    if ISBN10_RE.match(code):
        return "isbn"
    return "other"


def clean(raw_path: Path) -> tuple[pd.DataFrame, dict]:
    df = pd.read_csv(raw_path, dtype=str).rename(columns=RENAME)
    log = {"raw_rows": len(df)}

    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce")
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
    df["amount"] = df["unit_price"] * df["quantity"]
    df["asin"] = df["asin"].str.strip().str.upper()
    df["code_type"] = df["asin"].map(classify_code)
    log["bad_date_rows"] = int(df["order_date"].isna().sum())

    dup = df.duplicated()
    log["duplicate_rows"] = int(dup.sum())
    df = df[~dup]

    gift = df["category"].str.contains("GIFT_CARD", na=False) | df["title"].str.contains(
        "gift card", case=False, na=False
    )
    log["gift_card_rows"] = int(gift.sum())
    df = df[~gift]

    log["code_type_counts"] = df["code_type"].value_counts().to_dict()
    log["clean_rows"] = len(df)
    log["unique_asin"] = int(df.loc[df["code_type"] != "missing", "asin"].nunique())
    log["date_range"] = (str(df["order_date"].min().date()), str(df["order_date"].max().date()))
    return df, log


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", type=Path, default=RAW)
    ap.add_argument("--out", type=Path, default=OUT_DIR)
    args = ap.parse_args()

    df, log = clean(args.raw)
    args.out.mkdir(parents=True, exist_ok=True)
    df.to_parquet(args.out / "purchases.parquet", index=False)

    asin_list = (
        df[df["code_type"] != "missing"]
        .groupby(["asin", "code_type"])
        .agg(purchase_rows=("asin", "size"), top_category=("category", lambda s: s.mode().iat[0] if s.notna().any() else None))
        .reset_index()
        .sort_values("purchase_rows", ascending=False)
    )
    asin_list.to_csv(args.out / "asin_list.csv", index=False)

    for k, v in log.items():
        print(f"{k}: {v}")


if __name__ == "__main__":
    main()
