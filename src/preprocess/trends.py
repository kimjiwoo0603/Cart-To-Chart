"""A. Google Trends 전처리 (안서연)

data/raw/google_trends/*.csv (묶음 × 회차) ->
  data/interim/cleaned_trends/keyword_weekly.csv       키워드별 주간 값 (환산·3회 평균 후)
  data/interim/cleaned_trends/conversion_factors.csv   묶음·회차별 환산 계수와 주별 비율 분포
  data/processed/weekly_trends/weekly_trends.csv       6품목 × 261주
  data/processed/weekly_trends/spikes.csv              spike 목록
  logs/trends_qc.md                                    점검 결과 (실행할 때마다 새로 씀)

처리 순서 (결정 근거는 logs/preprocessing_log.md 2026-10-04 항목)
  1. "<1" -> 0.5, 빈 값 -> 결측
  2. 회차 = 묶음마다 받은 날짜순 번호. 묶음 b의 k회차는 묶음 1의 k회차 blanket으로 환산
     계수 = sum(묶음1 blanket) / sum(묶음b blanket)  (묶음당 상수 하나)
  3. 환산한 회차들을 평균 (결측은 빼고 평균)
  4. 매핑표로 product_type 부착, 한 품목에 키워드가 여러 개면 평균
  5. trends_yoy = trends - 52주 전 trends
  6. spike: 직전 12주 평균·표준편차(하한 1.0)로 z, z >= 2.
     앞 spike 주와 8주 미만 간격이면 같은 spike로 병합. is_spike는 병합된 spike의 첫 주에만 1.

사용법 (저장소 루트에서)
    python -m src.preprocess.trends
"""
from __future__ import annotations

import argparse
import datetime as dt
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from src.collect.google_trends import (ANCHOR, BUNDLES, RAW_DIR, fetched_date,
                                       identify_bundle, read_trends_csv)

ROOT = Path(__file__).resolve().parents[2]
INTERIM_DIR = ROOT / "data" / "interim" / "cleaned_trends"
OUT_DIR = ROOT / "data" / "processed" / "weekly_trends"
MAPPING_PATH = ROOT / "mapping" / "keyword_product_mapping.csv"
QC_PATH = ROOT / "logs" / "trends_qc.md"

FIRST_WEEK = "2017-12-31"  # 2018-01-01(월)이 속한 주의 일요일
N_WEEKS = 261
MAIN_PRODUCTS = ["TOILET_PAPER", "SURFACE_CLEANING_WIPE", "PUZZLES",
                 "BAKING_PAN", "BLANKET", "DRINKING_CUP"]

LESS_THAN_ONE = 0.5
RANGE_THRESHOLD = 20  # 원본 스케일에서 회차 간 최대-최소
YOY_LAG = 52
Z_WINDOW = 12
Z_THRESHOLD = 2.0
STD_FLOOR = 1.0
MERGE_GAP = 8  # 앞 spike 주와 이 값 미만 간격이면 병합


def expected_weeks() -> pd.DatetimeIndex:
    return pd.date_range(FIRST_WEEK, periods=N_WEEKS, freq="7D")


def to_numeric(s: pd.Series) -> pd.Series:
    s = s.astype(str).str.strip()
    s = s.mask(s == "<1", str(LESS_THAN_ONE)).replace("", np.nan)
    return pd.to_numeric(s, errors="raise")


@dataclass
class Run:
    bundle: int
    run: int  # 묶음 안에서 받은 날짜순 번호 (1부터)
    date: dt.date
    path: Path
    raw: pd.DataFrame  # 원본 문자열, index = week
    values: pd.DataFrame  # 숫자, index = 261주 전체
    missing_weeks: list[str]
    extra_weeks: list[str]


def load_runs(raw_dir: Path) -> dict[int, list[Run]]:
    weeks = expected_weeks()
    by_bundle: dict[int, list[tuple]] = {}
    for path in sorted(raw_dir.glob("*.csv")):
        df = read_trends_csv(path)
        b = identify_bundle(df.columns[1:])
        by_bundle.setdefault(b, []).append((fetched_date(path), path, df))

    runs: dict[int, list[Run]] = {}
    for b, items in sorted(by_bundle.items()):
        items.sort(key=lambda x: x[0])
        dates = [d for d, _, _ in items]
        if len(set(dates)) != len(dates):
            raise ValueError(f"묶음 {b}에 같은 날짜 파일이 2개 이상: {dates}")
        runs[b] = []
        for k, (d, path, df) in enumerate(items, 1):
            raw = df.set_index("week")
            idx = pd.DatetimeIndex(pd.to_datetime(raw.index))
            values = raw.apply(to_numeric)
            values.index = idx
            values = values.reindex(weeks)
            missing = sorted(set(weeks) - set(idx)) + list(values.index[values.isna().any(axis=1)])
            runs[b].append(Run(
                bundle=b, run=k, date=d, path=path, raw=raw, values=values,
                missing_weeks=sorted({w.strftime("%Y-%m-%d") for w in missing}),
                extra_weeks=sorted(w.strftime("%Y-%m-%d") for w in set(idx) - set(weeks)),
            ))
    if 1 not in runs:
        raise ValueError("묶음 1 파일이 없어 환산 기준을 정할 수 없음")
    for b, rs in runs.items():
        if len(rs) > len(runs[1]):
            raise ValueError(f"묶음 {b}의 회차({len(rs)})가 묶음 1({len(runs[1])})보다 많음")
    return runs


# ---------------------------------------------------------------- 점검

def peak_positions(runs: dict[int, list[Run]]) -> pd.DataFrame:
    """각 조회에서 100(정규화 기준)이 된 키워드와 주."""
    rows = []
    for b, rs in runs.items():
        for r in rs:
            hits = [(kw, week) for kw in r.raw.columns
                    for week in r.raw.index[r.raw[kw] == "100"]]
            rows.append({"bundle": b, "run": r.run, "run_date": r.date.isoformat(),
                         "peak": "; ".join(f"{kw} @ {w}" for kw, w in hits) or "(없음)"})
    df = pd.DataFrame(rows)
    df["peak_changed_in_bundle"] = df.groupby("bundle")["peak"].transform("nunique") > 1
    return df


def range_check(runs: dict[int, list[Run]]) -> pd.DataFrame:
    """원본 스케일에서 회차 간 최대-최소 > RANGE_THRESHOLD 인 주."""
    rows = []
    for b, rs in runs.items():
        if len(rs) < 2:
            continue
        for kw in rs[0].values.columns:
            stacked = pd.concat({r.run: r.values[kw] for r in rs}, axis=1)
            rng = stacked.max(axis=1) - stacked.min(axis=1)
            for week in rng.index[rng > RANGE_THRESHOLD]:
                rows.append({"bundle": b, "keyword": kw,
                             "week": week.strftime("%Y-%m-%d"),
                             "values": " / ".join(f"{v:g}" for v in stacked.loc[week]),
                             "range": rng[week]})
    return pd.DataFrame(rows, columns=["bundle", "keyword", "week", "values", "range"])


# ---------------------------------------------------------------- 환산·평균

def conversion_factors(runs: dict[int, list[Run]]) -> pd.DataFrame:
    rows = []
    for b, rs in runs.items():
        for r in rs:
            ref_run = runs[1][r.run - 1]
            ref, own = ref_run.values[ANCHOR], r.values[ANCHOR]
            ok = ref.notna() & own.notna() & (own > 0)
            ratio = ref[ok] / own[ok]
            rows.append({
                "bundle": b, "run": r.run, "run_date": r.date.isoformat(),
                "ref_date": ref_run.date.isoformat(),
                "factor": ref[ok].sum() / own[ok].sum(),
                "ratio_mean": ratio.mean(), "ratio_median": ratio.median(),
                "ratio_cv": ratio.std() / ratio.mean(),
                "ratio_min": ratio.min(), "ratio_max": ratio.max(),
                "n_weeks": int(ok.sum()),
            })
    return pd.DataFrame(rows)


def keyword_weekly(runs: dict[int, list[Run]], factors: pd.DataFrame) -> pd.DataFrame:
    """회차별 환산 후 평균. blanket은 기준 묶음(1)의 값을 쓴다."""
    f = factors.set_index(["bundle", "run"])["factor"]
    frames = []
    for b, rs in runs.items():
        keywords = [k for k in rs[0].values.columns if b == 1 or k != ANCHOR]
        for kw in keywords:
            stacked = pd.concat({r.run: r.values[kw] * f[(b, r.run)] for r in rs}, axis=1)
            frames.append(pd.DataFrame({
                "week": stacked.index, "keyword": kw, "bundle": b,
                "trends": stacked.mean(axis=1, skipna=True),
                "n_runs": stacked.notna().sum(axis=1),
            }))
    return pd.concat(frames, ignore_index=True)


# ---------------------------------------------------------------- 품목·YoY·spike

def product_weekly(kw: pd.DataFrame, mapping: pd.DataFrame) -> pd.DataFrame:
    mapping = mapping.assign(keyword=mapping["keyword"].str.strip().str.lower())
    unmapped = sorted(set(kw["keyword"]) - set(mapping["keyword"]))
    if unmapped:
        raise ValueError(f"매핑표에 없는 키워드: {unmapped}")
    merged = kw.merge(mapping[["keyword", "product_type"]], on="keyword")
    order = {k: i for i, k in enumerate(mapping["keyword"])}
    labels = (merged.drop_duplicates(["product_type", "keyword"])
              .assign(o=lambda d: d["keyword"].map(order))
              .sort_values("o").groupby("product_type")["keyword"]
              .agg("|".join))
    out = (merged.groupby(["product_type", "week"], as_index=False)["trends"].mean())
    out["keyword"] = out["product_type"].map(labels)
    return out


def rolling_z(x: pd.Series) -> tuple[pd.Series, pd.Series]:
    """직전 Z_WINDOW주(이번 주 제외) 평균·표준편차로 z. 12주가 다 차야 계산."""
    prev = x.shift(1).rolling(Z_WINDOW, min_periods=Z_WINDOW)
    mu = prev.mean()
    sd = prev.std().clip(lower=STD_FLOOR)
    return (x - mu) / sd, mu


def detect_spikes(weeks: pd.Series, x: pd.Series) -> tuple[pd.Series, list[dict]]:
    """z >= 2 인 주를 찾아 연쇄 병합. (첫 주 표시, spike 목록) 반환."""
    x = x.reset_index(drop=True)
    weeks = weeks.reset_index(drop=True)
    z, mu = rolling_z(x)
    flagged = np.flatnonzero((z >= Z_THRESHOLD).to_numpy())

    episodes: list[list[int]] = []
    for i in flagged:
        if episodes and i - episodes[-1][-1] < MERGE_GAP:
            episodes[-1].append(i)
        else:
            episodes.append([i])

    is_spike = pd.Series(0, index=x.index, dtype="int64")
    records = []
    for n, ep in enumerate(episodes, 1):
        start, end = ep[0], ep[-1]
        span = x.iloc[start:end + 1]
        peak = span.idxmax()
        is_spike.iloc[start] = 1
        records.append({
            "spike_no": n,
            "start_week": weeks[start], "peak_week": weeks[peak], "end_week": weeks[end],
            "length_weeks": end - start + 1, "n_flagged_weeks": len(ep),
            "baseline_mean": mu[start], "start_value": x[start], "peak_value": x[peak],
            "start_z": z[start], "max_z": z.iloc[ep].max(),
        })
    return is_spike, records


def build_outputs(prod: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    parts, spike_rows = [], []
    for pt, g in prod.groupby("product_type", sort=False):
        g = g.sort_values("week").reset_index(drop=True)
        g["trends_yoy"] = g["trends"] - g["trends"].shift(YOY_LAG)
        week_str = g["week"].dt.strftime("%Y-%m-%d")
        for col, basis in (("is_spike", "trends"), ("is_spike_yoy", "trends_yoy")):
            flags, recs = detect_spikes(week_str, g[basis])
            g[col] = flags
            spike_rows += [{"product_type": pt, "keyword": g["keyword"].iloc[0],
                            "basis": basis, **r} for r in recs]
        parts.append(g)

    weekly = pd.concat(parts, ignore_index=True)
    weekly["week"] = weekly["week"].dt.strftime("%Y-%m-%d")
    weekly = weekly[["week", "keyword", "product_type", "trends", "trends_yoy",
                     "is_spike", "is_spike_yoy"]]
    spikes = pd.DataFrame(spike_rows, columns=[
        "product_type", "keyword", "basis", "spike_no", "start_week", "peak_week",
        "end_week", "length_weeks", "n_flagged_weeks", "baseline_mean",
        "start_value", "peak_value", "start_z", "max_z"])
    return weekly, spikes


# ---------------------------------------------------------------- 보고서

def md_table(df: pd.DataFrame, floatfmt: str = ".3f") -> str:
    if df.empty:
        return "(없음)\n"
    def fmt(v):
        if isinstance(v, (float, np.floating)):
            return "" if pd.isna(v) else format(v, floatfmt)
        return str(v)
    lines = ["| " + " | ".join(map(str, df.columns)) + " |",
             "|" + "---|" * len(df.columns)]
    lines += ["| " + " | ".join(fmt(v) for v in row) + " |"
              for row in df.itertuples(index=False)]
    return "\n".join(lines) + "\n"


def write_qc(path: Path, runs, peaks, factors, ranges, kw, weekly, spikes) -> None:
    files = pd.DataFrame([{"bundle": r.bundle, "run": r.run, "run_date": r.date.isoformat(),
                           "file": r.path.name, "missing_weeks": len(r.missing_weeks),
                           "extra_weeks": len(r.extra_weeks)}
                          for rs in runs.values() for r in rs])
    missing = pd.DataFrame([{"bundle": r.bundle, "run": r.run, "weeks": ", ".join(r.missing_weeks)}
                            for rs in runs.values() for r in rs if r.missing_weeks])
    n_runs = kw.groupby("keyword")["n_runs"].agg(["min", "max"]).reset_index()
    summary = (spikes.groupby(["product_type", "basis"]).size().unstack(fill_value=0)
               .reindex(MAIN_PRODUCTS).fillna(0).astype(int).reset_index()
               if not spikes.empty else spikes)

    text = f"""# Google Trends 전처리 점검 결과

`python -m src.preprocess.trends` 실행 시 자동 생성 ({dt.datetime.now():%Y-%m-%d %H:%M}). 결정 사항은 `preprocessing_log.md` 참고.

## 입력 파일
{md_table(files)}
## 결측 주 (0으로 채우지 않고 결측으로 둠)
{md_table(missing)}
## 정규화 기준(100) 위치
회차마다 100이 된 키워드·주가 바뀐 묶음은 회차별로 스케일이 다르다는 뜻이고, 회차별 환산 후 평균하는 근거가 된다.

{md_table(peaks)}
## 환산 계수와 주별 비율 분포
`factor` = sum(묶음 1 blanket) / sum(이 묶음 blanket), 같은 회차끼리. `ratio_*`는 주별 비율(묶음 1 blanket_t / 이 묶음 blanket_t)의 분포. CV가 작고 min~max가 좁으면 상수 하나로 환산해도 된다는 근거다.

{md_table(factors, ".4f")}
## 회차 간 차이 > {RANGE_THRESHOLD} (원본 스케일)
{md_table(ranges, ".1f")}
## 키워드별 평균에 쓴 회차 수
{md_table(n_runs)}
## 출력
- weekly_trends.csv: {len(weekly)}행, 품목 {weekly['product_type'].nunique()}개, 주 {weekly['week'].nunique()}개 ({weekly['week'].min()} ~ {weekly['week'].max()})
- spikes.csv: {len(spikes)}건

### 품목별 spike 수 (RQ3 유행형/꾸준형 분류용)
{md_table(summary)}"""
    path.write_text(text, encoding="utf-8")


# ---------------------------------------------------------------- 실행

def run(raw_dir: Path = RAW_DIR, interim_dir: Path = INTERIM_DIR, out_dir: Path = OUT_DIR,
        mapping_path: Path = MAPPING_PATH, qc_path: Path = QC_PATH) -> None:
    runs = load_runs(raw_dir)
    peaks = peak_positions(runs)
    ranges = range_check(runs)
    factors = conversion_factors(runs)
    kw = keyword_weekly(runs, factors)

    mapping = pd.read_csv(mapping_path, dtype=str, keep_default_na=False)
    prod = product_weekly(kw, mapping)
    absent = [p for p in MAIN_PRODUCTS if p not in set(prod["product_type"])]
    if absent:
        print(f"경고: 데이터가 없는 품목 {absent}")
    prod = prod[prod["product_type"].isin(MAIN_PRODUCTS)]
    prod = prod.assign(o=prod["product_type"].map(MAIN_PRODUCTS.index)).sort_values(["o", "week"]).drop(columns="o")
    weekly, spikes = build_outputs(prod)

    expected = len(MAIN_PRODUCTS) * N_WEEKS
    if len(weekly) != expected or weekly["week"].min() != FIRST_WEEK:
        print(f"경고: weekly_trends {len(weekly)}행 (기대 {expected}), 첫 주 {weekly['week'].min()}")

    interim_dir.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)
    kw_out = kw.assign(week=kw["week"].dt.strftime("%Y-%m-%d"))
    kw_out.to_csv(interim_dir / "keyword_weekly.csv", index=False)
    factors.to_csv(interim_dir / "conversion_factors.csv", index=False)
    weekly.to_csv(out_dir / "weekly_trends.csv", index=False)
    spikes.to_csv(out_dir / "spikes.csv", index=False)
    write_qc(qc_path, runs, peaks, factors, ranges, kw, weekly, spikes)

    print(f"weekly_trends.csv {len(weekly)}행, spikes.csv {len(spikes)}건, 점검 결과 {qc_path}")
    if peaks["peak_changed_in_bundle"].any():
        print("  회차마다 100 위치가 바뀐 묶음 있음 (점검 결과 참고)")
    if not ranges.empty:
        print(f"  회차 간 차이 > {RANGE_THRESHOLD}: {len(ranges)}건")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--raw-dir", type=Path, default=RAW_DIR)
    p.add_argument("--interim-dir", type=Path, default=INTERIM_DIR)
    p.add_argument("--out-dir", type=Path, default=OUT_DIR)
    p.add_argument("--mapping", type=Path, default=MAPPING_PATH)
    p.add_argument("--qc", type=Path, default=QC_PATH)
    args = p.parse_args()
    run(args.raw_dir, args.interim_dir, args.out_dir, args.mapping, args.qc)


if __name__ == "__main__":
    main()
