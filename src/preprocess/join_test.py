"""Open E-commerce ↔ Amazon Reviews 2023 조인 가능성 테스트.

구매 데이터의 ASIN을 리뷰의 `asin`, `parent_asin` 각각과 매칭해서 매칭률을 계산한다.
리뷰 파일은 카테고리 하나도 수십 GB라서 메모리에 올리지 않고 한 줄씩 스트리밍하면서
구매 ASIN과 맞는 리뷰만 남긴다. 로컬 파일 경로와 URL 모두 받는다 (.gz 여부 자동 판별).

실행 예:
  python -m src.preprocess.clean_purchases
  python -m src.preprocess.join_test --category Home_and_Kitchen \
      --reviews https://mcauleylab.ucsd.edu/public_datasets/data/amazon_2023/raw/review_categories/Home_and_Kitchen.jsonl.gz

출력:
  data/interim/filtered_reviews/<category>_matched_reviews.parquet  매칭된 리뷰
  logs/join_test_<category>.md                                      결과 표
"""
import argparse
import gzip
import io
import json
import re
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

ASIN_LIST = Path("data/interim/cleaned_purchase/asin_list.csv")
OUT_DIR = Path("data/interim/filtered_reviews")
LOG_DIR = Path("logs")
KEEP = ["asin", "parent_asin", "rating", "title", "text", "timestamp",
        "helpful_vote", "verified_purchase", "user_id"]
ASIN_FIELD = re.compile(r'"asin":\s*"([^"]+)"')
PARENT_FIELD = re.compile(r'"parent_asin":\s*"([^"]+)"')
BATCH = 50_000


def open_lines(src: str):
    """로컬 경로 또는 URL을 한 줄씩 읽는 텍스트 스트림으로 연다."""
    if src.startswith("http"):
        import requests
        resp = requests.get(src, stream=True, timeout=60)
        resp.raise_for_status()
        resp.raw.decode_content = True
        raw = resp.raw
        if src.endswith(".gz"):
            raw = gzip.GzipFile(fileobj=raw)
        return io.TextIOWrapper(raw, encoding="utf-8")
    if src.endswith(".gz"):
        return gzip.open(src, "rt", encoding="utf-8")
    return open(src, encoding="utf-8")


def stream_matches(src: str, purchase_asins: set, out_path: Path, progress_every=5_000_000):
    """리뷰를 스트리밍하며 구매 ASIN과 맞는 리뷰만 parquet로 저장하고 매칭 집합을 돌려준다."""
    by_asin, by_parent = set(), set()
    asin_to_parent = {}
    total = kept = 0
    rows, writer = [], None
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with open_lines(src) as f:
        for line in f:
            total += 1
            if total % progress_every == 0:
                print(f"  {total:,} lines read, {kept:,} kept")
            a = ASIN_FIELD.search(line)
            p = PARENT_FIELD.search(line)
            a = a.group(1) if a else None
            p = p.group(1) if p else None
            hit_a, hit_p = a in purchase_asins, p in purchase_asins
            if not (hit_a or hit_p):
                continue
            if hit_a:
                by_asin.add(a)
                asin_to_parent[a] = p
            if hit_p:
                by_parent.add(p)
            rec = json.loads(line)
            rows.append({k: rec.get(k) for k in KEEP})
            kept += 1
            if len(rows) >= BATCH:
                writer = _flush(rows, writer, out_path)
                rows = []
    if rows or writer is None:
        writer = _flush(rows, writer, out_path)
    writer.close()
    return {"total_reviews": total, "matched_reviews": kept,
            "by_asin": by_asin, "by_parent": by_parent, "asin_to_parent": asin_to_parent}


def _flush(rows, writer, out_path):
    df = pd.DataFrame(rows, columns=KEEP).astype({"asin": str, "parent_asin": str, "title": str, "text": str, "user_id": str})
    table = pa.Table.from_pandas(df, preserve_index=False)
    if writer is None:
        writer = pq.ParquetWriter(out_path, table.schema)
    writer.write_table(table)
    return writer


def summarize(asins: pd.DataFrame, res: dict, category: str) -> str:
    valid = asins[asins["code_type"] == "asin"]
    all_codes = set(asins["asin"])
    n_all, n_valid = len(all_codes), valid["asin"].nunique()
    m_a, m_p = res["by_asin"], res["by_parent"]
    m_any = m_a | m_p

    def pct(n, d):
        return f"{n:,} / {d:,} ({n / d:.1%})" if d else "0"

    asins = asins.assign(matched=asins["asin"].isin(m_any))
    rows_all = asins["purchase_rows"].sum()
    rows_hit = asins.loc[asins["matched"], "purchase_rows"].sum()

    unmatched = asins[~asins["matched"]]
    reasons = {
        "ISBN(도서) 코드": int((unmatched["code_type"] == "isbn").sum()),
        "ASIN 형식 아님": int((unmatched["code_type"] == "other").sum()),
        f"정상 ASIN이지만 {category} 리뷰에 없음 (다른 카테고리이거나 리뷰 없음)":
            int((unmatched["code_type"] == "asin").sum()),
    }

    by_cat = (asins[asins["code_type"] == "asin"]
              .groupby("top_category")
              .agg(asin_n=("asin", "size"), matched=("matched", "sum"))
              .assign(rate=lambda d: d["matched"] / d["asin_n"])
              .sort_values("matched", ascending=False).head(15))

    same_parent = sum(1 for a, p in res["asin_to_parent"].items() if a == p)
    lines = [
        f"# 조인 가능성 테스트: {category}", "",
        "| 항목 | 결과 |", "| --- | --- |",
        f"| 테스트 카테고리 | {category} |",
        f"| 리뷰 수 (스트리밍한 전체) | {res['total_reviews']:,} |",
        f"| 구매 데이터 고유 코드 수 | {n_all:,} (정상 ASIN {n_valid:,}) |",
        f"| Reviews `asin` 매칭 | {pct(len(m_a), n_valid)} |",
        f"| Reviews `parent_asin` 매칭 | {pct(len(m_p), n_valid)} |",
        f"| 둘 중 하나라도 매칭 | {pct(len(m_any), n_valid)} |",
        f"| 매칭된 구매 행 비율 | {pct(int(rows_hit), int(rows_all))} |",
        f"| 매칭된 리뷰 수 | {res['matched_reviews']:,} |",
        f"| `asin`으로 매칭된 것 중 asin == parent_asin | {pct(same_parent, len(m_a))} |",
        "", "## 매칭 실패 사유 (고유 코드 기준)", "",
        "| 사유 | 코드 수 |", "| --- | --- |",
        *[f"| {k} | {v:,} |" for k, v in reasons.items()],
        "", "## 구매 데이터 카테고리별 매칭 (상위 15)", "",
        "| Open E-commerce 카테고리 | 정상 ASIN 수 | 매칭 | 매칭률 |", "| --- | --- | --- | --- |",
        *[f"| {c} | {int(r.asin_n):,} | {int(r.matched):,} | {r.rate:.1%} |" for c, r in by_cat.iterrows()],
        "",
        "매칭률의 분모는 구매 데이터 전체 카테고리의 ASIN이므로, 한 카테고리만 받은 상태에서는 "
        "전체 매칭률이 낮게 나오는 것이 정상이다. 카테고리별 표에서 해당 카테고리 상품의 매칭률을 본다.",
    ]
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--category", required=True, help="예: Home_and_Kitchen")
    ap.add_argument("--reviews", required=True, help="리뷰 jsonl(.gz) 경로 또는 URL")
    ap.add_argument("--asin-list", type=Path, default=ASIN_LIST)
    args = ap.parse_args()

    asins = pd.read_csv(args.asin_list, dtype={"asin": str})
    purchase_asins = set(asins["asin"])
    print(f"구매 ASIN {len(purchase_asins):,}개로 {args.category} 리뷰 스트리밍 시작")

    out = OUT_DIR / f"{args.category}_matched_reviews.parquet"
    res = stream_matches(args.reviews, purchase_asins, out)
    report = summarize(asins, res, args.category)

    LOG_DIR.mkdir(exist_ok=True)
    (LOG_DIR / f"join_test_{args.category}.md").write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
