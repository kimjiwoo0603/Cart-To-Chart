# B. Open E-commerce 구매 데이터 전처리

import pandas as pd
import numpy as np
from pathlib import Path

# ============================================================
# 0. 경로 및 기본 설정
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]   # 저장소 최상위 폴더

RAW_PATH = BASE_DIR / "data" / "raw" / "open_ecommerce" / "amazon-purchases.csv"

CLEANED_PATH = BASE_DIR / "data" / "interim" / "cleaned_purchase" / "purchases_clean_2018_2022.csv"
WEEKLY_PATH  = BASE_DIR / "data" / "processed" / "weekly_purchase" / "weekly_purchase.csv"
ASIN_PATH    = BASE_DIR / "data" / "processed" / "asin_list.csv"

START_DATE = pd.Timestamp("2018-01-01")
END_DATE = pd.Timestamp("2022-12-31")

# 프로젝트에서 분석할 6개 상품 유형
TARGET_PRODUCTS = [
    "TOILET_PAPER",
    "SURFACE_CLEANING_WIPE",
    "PUZZLES",
    "BAKING_PAN",
    "BLANKET",
    "DRINKING_CUP"
]


# 출력 폴더가 없으면 자동으로 생성
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# 1. 원본 데이터 불러오기
# ============================================================
# 원본 구매 데이터에는 구매일, 상품 가격, 수량,
# ASIN, Category, Survey ResponseID 등의 정보가 포함

df = pd.read_csv(RAW_PATH)

print("원본 데이터")
print("행 수:", len(df))
print("컬럼:", df.columns.tolist())


# ============================================================
# 2. 데이터 형식 변환
# ============================================================
# Order Date를 날짜 형식으로 변환

df["Order Date"] = pd.to_datetime(df["Order Date"])

print("\n원본 데이터의 날짜 범위:")
print(df["Order Date"].min(), "~", df["Order Date"].max())


# ============================================================
# 3. 기프트카드 구매 기록 제외
# ============================================================
# 프로젝트에서는 일반 상품의 구매 추세를 분석하기 때문에
# 기프트카드에 해당하는 구매 기록을 제외
#
# Category가 기프트카드에 해당하거나
# 상품명(Title)에 "GIFT CARD"가 포함된 경우 제외

gift_card_categories = [
    "ABIS_GIFT_CARD",
    "CONSUMABLES_EMAIL_GIFT_CARD",
    "ELECTRONIC_GIFT_CARD",
    "ELECTRONIC_GIFT_XXRD",
    "ECARD GIFT CERTIFICATE",
    "GIFT_CARD",
    "GIFT_XXRD",
    "NONACTIVATED_GIFT_CARD",
    "PHYSICAL_GIFT_CARD"
]

gift_card_category_mask = (
    df["Category"].isin(gift_card_categories)
)

# 전: Category 조건 OR 제목 조건
# 후: Category 조건만
gift_card_mask = gift_card_category_mask

print("\n제외된 기프트카드 구매 기록:", gift_card_mask.sum())

df = df.loc[~gift_card_mask].copy()

print("기프트카드 제외 후 행 수:", len(df))


# ============================================================
# 4. 분석 기간 제한
# ============================================================
# 프로젝트의 분석 기간인
# 2018-01-01 ~ 2022-12-31만 사용

df = df[
    (df["Order Date"] >= START_DATE) &
    (df["Order Date"] <= END_DATE)
].copy()

print("\n분석 기간 필터링 후 행 수:", len(df))
print(
    "분석 기간:",
    df["Order Date"].min(),
    "~",
    df["Order Date"].max()
)


# ============================================================
# 5. 주요 결측치 확인
# ============================================================
# 리뷰 데이터와 조인하기 위해 ASIN이 필요
# 상품 유형별 분석을 위해 Category가 필요

print("\n결측치 확인:")
print(
    df[
        [
            "ASIN/ISBN (Product Code)",
            "Category"
        ]
    ].isna().sum()
)


# ============================================================
# 6. ASIN 또는 Category가 없는 행 제거
# ============================================================
# ASIN이 없는 행:
# → 리뷰 데이터와 연결할 수 없기 때문에 제거
#
# Category가 없는 행:
# → 어떤 상품 유형인지 알 수 없기 때문에 제거

missing_asin = df["ASIN/ISBN (Product Code)"].isna()
missing_category = df["Category"].isna()

print("\nASIN 결측 행:", missing_asin.sum())
print("Category 결측 행:", missing_category.sum())
print(
    "제거할 행:",
    (missing_asin | missing_category).sum()
)

df = df[
    ~(
        missing_asin |
        missing_category
    )
].copy()

print("결측치 제거 후 행 수:", len(df))


# ============================================================
# 7. 완전히 동일한 중복 행 제거
# ============================================================
# 모든 컬럼의 값이 동일한 행을 완전 중복으로 판단하여 제거

duplicate_count = df.duplicated().sum()

print("\n완전 중복 행:", duplicate_count)

df = df.drop_duplicates().copy()

print("중복 제거 후 행 수:", len(df))


# ============================================================
# 8. ASIN 형식 통일
# ============================================================
# ASIN 앞뒤의 공백을 제거
# 모든 ASIN을 대문자로 통일

df["ASIN/ISBN (Product Code)"] = (
    df["ASIN/ISBN (Product Code)"]
    .str.strip()
    .str.upper()
)


# ============================================================
# 9. 이상치 확인 및 표시
# ============================================================
# 다음 조건에 해당하는 구매 기록을 이상치로 표시
#
# - 상품 단가가 $1,000 초과
# - 구매 수량이 10개 초과
#
# 이상치는 임의로 삭제하지 않고 is_outlier 컬럼으로 표시

df["is_outlier"] = (
    (df["Purchase Price Per Unit"] > 1000) |
    (df["Quantity"] > 10)
)

print("\n이상치로 표시된 행:", df["is_outlier"].sum())

print(
    df["is_outlier"]
    .value_counts()
    .rename({
        False: "정상",
        True: "이상치"
    })
)


# ============================================================
# 10. 최종 정제 데이터 저장
# ============================================================

print("\n최종 정제 데이터")
print("행 수:", len(df))
print("컬럼:", df.columns.tolist())

df.to_csv(
    CLEANED_PATH,
    index=False
)

print("\n저장 완료:", CLEANED_PATH)


# ============================================================
# 11. 분석 대상 6개 상품만 선택
# ============================================================
# 프로젝트에서 최종적으로 분석하는 6개 상품 유형만 추출

df_target = df[
    df["Category"].isin(TARGET_PRODUCTS)
].copy()

print("\n분석 대상 상품 데이터")
print("행 수:", len(df_target))

print(
    df_target["Category"]
    .value_counts()
    .sort_index()
)


# ============================================================
# 12. 일요일 시작 기준으로 주차 생성
# ============================================================
# 각 구매 기록을 해당 주의 일요일 날짜에 대응
#
# 예:
# 2019-09-28 → 2019-09-22
# 2019-01-02 → 2018-12-30

df_target["week"] = (
    df_target["Order Date"]
    - pd.to_timedelta(
        (df_target["Order Date"].dt.dayofweek + 1) % 7,
        unit="D"
    )
)

print("\n주차 범위:")
print(
    df_target["week"].min(),
    "~",
    df_target["week"].max()
)


# ============================================================
# 13. 주간 구매 데이터 집계
# ============================================================
# purchase_count:
# 해당 주의 구매 기록 수
#
# quantity_sum:
# 해당 주에 실제로 구매된 상품 수량의 합

weekly_purchase = (
    df_target
    .groupby(["week", "Category"])
    .agg(
        purchase_count=("Category", "size"),
        quantity_sum=("Quantity", "sum")
    )
    .reset_index()
    .rename(columns={
        "Category": "product_type"
    })
)

print("\n희소 주간 데이터")
print("행 수:", len(weekly_purchase))


# ============================================================
# 14. 모든 주차 × 상품 조합 생성
# ============================================================
# 특정 상품의 구매가 없는 주도 데이터에 포함하기 위해
# 모든 주차와 6개 상품의 조합을 생성
#
# 구매가 없는 경우 purchase_count와 quantity_sum은 0으로 채움

all_weeks = pd.date_range(
    start=weekly_purchase["week"].min(),
    end=weekly_purchase["week"].max(),
    freq="W-SUN"
)

full_index = pd.MultiIndex.from_product(
    [all_weeks, TARGET_PRODUCTS],
    names=["week", "product_type"]
)

weekly_full = (
    weekly_purchase
    .set_index(["week", "product_type"])
    .reindex(full_index, fill_value=0)
    .reset_index()
)

print("\n완성된 주간 데이터")
print("행 수:", len(weekly_full))
print("주 수:", weekly_full["week"].nunique())
print("상품 수:", weekly_full["product_type"].nunique())


# ============================================================
# 15. 활동 응답자 수 계산
# ============================================================
# 전체 구매 데이터에서 각 응답자의
# 첫 구매일과 마지막 구매일을 계산
#
# 활동 응답자:
# 첫 구매일 <= 해당 주차 <= 마지막 구매일
#
# 활동 응답자 수는 6개 상품만을 기준으로 계산하지 않고
# 전체 정제 구매 데이터를 기준으로 계산

respondent_period = (
    df.groupby("Survey ResponseID")["Order Date"]
    .agg(
        first_purchase="min",
        last_purchase="max"
    )
    .reset_index()
)

print(
    "\n응답자 수:",
    len(respondent_period)
)

active_by_week = pd.DataFrame({
    "week": all_weeks
})

active_by_week["active_respondents"] = (
    active_by_week["week"]
    .apply(
        lambda week: (
            (respondent_period["first_purchase"] <= week + pd.Timedelta(days=6)) &
            (respondent_period["last_purchase"] >= week)
        ).sum()
    )
)

print("\n활동 응답자 수 범위:")
print(
    active_by_week["active_respondents"].min(),
    "~",
    active_by_week["active_respondents"].max()
)


# ============================================================
# 16. 구매율 계산
# ============================================================
# 구매율은 활동 응답자 수의 차이를 보정하기 위해 계산
#
# purchase_rate =
# purchase_count / active_respondents × 1,000
#
# 활동 응답자가 0명인 경우 구매율을 계산할 수 없으므로
# 결측값으로 처리

weekly_full = weekly_full.merge(
    active_by_week,
    on="week",
    how="left"
)

weekly_full["purchase_rate"] = (
    weekly_full["purchase_count"]
    / weekly_full["active_respondents"]
    * 1000
)

weekly_full.loc[
    weekly_full["active_respondents"] == 0,
    "purchase_rate"
] = pd.NA


# ============================================================
# 17. 최종 주간 구매 데이터 구성
# ============================================================
# 최종적으로 필요한 컬럼만 남김

weekly_final = weekly_full[
    [
        "week",
        "product_type",
        "purchase_count",
        "quantity_sum",
        "purchase_rate"
    ]
].copy()

print("\n최종 주간 구매 데이터")
print("행 수:", len(weekly_final))
print("컬럼:", weekly_final.columns.tolist())


# ============================================================
# 18. 주간 구매 데이터 저장
# ============================================================

weekly_final.to_csv(
    WEEKLY_PATH,
    index=False
)

print("저장 완료:", WEEKLY_PATH)


# ============================================================
# 19. ASIN과 상품 유형의 일관성 확인
# ============================================================
# 하나의 ASIN이 여러 Category에 연결되어 있는지 확인

asin_category_check = (
    df_target
    .groupby("ASIN/ISBN (Product Code)")["Category"]
    .nunique()
)

multi_category_asins = (
    asin_category_check[
        asin_category_check > 1
    ]
    .index
)

print(
    "\n여러 상품 유형에 연결된 ASIN 수:",
    len(multi_category_asins)
)

print(
    "해당 ASIN:",
    multi_category_asins.tolist()
)


# ============================================================
# 20. 잘못 분류된 ASIN 기록 처리
# ============================================================
# B005NIKG4E는 SURFACE_CLEANING_WIPE와 DRINKING_CUP
# 두 Category에 연결되어 있음
#
# 해당 상품의 Title을 확인한 결과 렌즈 세정용 물티슈에 해당하므로
# ASIN 목록을 만들 때 DRINKING_CUP 기록을 제외
#
# 주간 구매 데이터 자체에서는 해당 기록을 삭제하지 않음

df_target_asin = df_target[
    ~(
        (df_target["ASIN/ISBN (Product Code)"] == "B005NIKG4E") &
        (df_target["Category"] == "DRINKING_CUP")
    )
].copy()

print(
    "\nASIN 목록 생성 전 행 수:",
    len(df_target_asin)
)


# ============================================================
# 21. ASIN 목록 생성
# ============================================================
# 리뷰 데이터와 구매 데이터를 연결할 때 사용할 ASIN 목록
#
# asin:
# 상품의 ASIN
#
# product_type:
# 상품 유형
#
# purchase_rows:
# 해당 ASIN의 구매 기록 수

asin_list = (
    df_target_asin
    .groupby(
        [
            "ASIN/ISBN (Product Code)",
            "Category"
        ]
    )
    .size()
    .reset_index(name="purchase_rows")
    .rename(columns={
        "ASIN/ISBN (Product Code)": "asin",
        "Category": "product_type"
    })
)

print("\nASIN 목록")
print("행 수:", len(asin_list))

print(
    asin_list
    .groupby("product_type")
    .size()
    .sort_index()
)


# ============================================================
# 22. ASIN 목록 저장
# ============================================================

asin_list.to_csv(
    ASIN_PATH,
    index=False
)

print("저장 완료:", ASIN_PATH)


# ============================================================
# 23. 최종 검증
# ============================================================

print("\n" + "=" * 60)
print("최종 검증")
print("=" * 60)


print("\n[주간 구매 데이터]")

print("행 수:", len(weekly_final))
print("상품 수:", weekly_final["product_type"].nunique())
print("주 수:", weekly_final["week"].nunique())

print(
    "purchase_count 결측:",
    weekly_final["purchase_count"].isna().sum()
)

print(
    "quantity_sum 결측:",
    weekly_final["quantity_sum"].isna().sum()
)

print(
    "purchase_rate 결측:",
    weekly_final["purchase_rate"].isna().sum()
)


print("\n[ASIN 목록]")

print("행 수:", len(asin_list))

print(
    "ASIN 중복:",
    asin_list["asin"].duplicated().sum()
)

print(
    "product_type 결측:",
    asin_list["product_type"].isna().sum()
)

print(
    "purchase_rows 결측:",
    asin_list["purchase_rows"].isna().sum()
)

print(
    "purchase_rows <= 0:",
    (asin_list["purchase_rows"] <= 0).sum()
)


print("\n" + "=" * 60)
print("B. 구매 데이터 전처리 완료")
print("=" * 60)
