"""A. Google Trends 수집 (안서연)

기준 키워드 blanket + 키워드 최대 4개를 한 묶음으로 받아
data/raw/google_trends/<keyword>_<받은날짜>.csv 로 원본 그대로 저장한다.

- 조회 조건 고정: 미국, 2018-01-01 ~ 2022-12-31, 카테고리 전체, 웹 검색 (주 단위로 나옴)
- 저장 형식은 trends.google.com에서 수동으로 내려받은 CSV와 같다
  (상단 "Category: ..." 줄, 빈 줄, "Week,<키워드>: (United States),..." 헤더, "<1" 문자열 유지).
  그래서 수동 다운로드 파일과 pytrends로 받은 파일을 read_trends_csv 하나로 읽는다.
- pytrends의 interest_over_time()은 "<1"을 0으로 바꿔 버려서 진짜 0과 구분이 안 된다.
  같은 요청을 직접 보내고 응답의 formattedValue("<1" 그대로)를 저장한다.

사용법 (저장소 루트에서)
    python -m src.collect.google_trends                    # 오늘 날짜로 모든 묶음 받기
    python -m src.collect.google_trends --bundles 2 3      # 일부 묶음만
    python -m src.collect.google_trends --import multiTimeline.csv --date 2026-10-02
                                                           # 수동 다운로드 파일을 규칙에 맞는 이름으로 복사
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import io
import json
import random
import re
import shutil
import time
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw" / "google_trends"

# 조회 조건 (명세 3장 1번)
GEO = "US"
GEO_LABEL = "United States"
TIMEFRAME = "2018-01-01 2022-12-31"
CATEGORY = 0  # 전체
GPROP = ""  # 웹 검색

# 기준 키워드는 모든 묶음의 맨 앞에 들어간다 (명세 3장 2번)
ANCHOR = "blanket"
# 묶음 1·2 = 명세 1장 키워드 7개, 묶음 3 = 예비 품목 2개
BUNDLES: dict[int, list[str]] = {
    1: ["toilet paper", "disinfecting wipes", "jigsaw puzzle", "baking pan"],
    2: ["baking", "weighted blanket", "tumbler"],
    3: ["air purifier", "air fryer"],
}

DATE_IN_NAME = re.compile(r"_(\d{4}-\d{2}-\d{2})\.csv$")
TIME_HEADERS = {"week", "day", "month", "time", "date"}

# 재시도·대기 (초)
MAX_RETRIES = 6
BASE_WAIT = 60
MAX_WAIT = 30 * 60
BETWEEN_BUNDLES = (20, 40)


def bundle_keywords(bundle: int) -> list[str]:
    return [ANCHOR] + BUNDLES[bundle]


def identify_bundle(keywords) -> int:
    """키워드 목록(순서 무관)이 어느 묶음인지 찾는다."""
    kw_set = {k.strip().lower() for k in keywords}
    for b in BUNDLES:
        if kw_set == set(bundle_keywords(b)):
            return b
    raise ValueError(f"정의된 묶음과 키워드가 맞지 않음: {sorted(kw_set)}")


def raw_filename(keywords: list[str], fetched: dt.date) -> str:
    """blanket+toilet-paper+..._2026-10-04.csv"""
    slug = "+".join(k.replace(" ", "-") for k in keywords)
    return f"{slug}_{fetched.isoformat()}.csv"


def fetched_date(path: Path) -> dt.date:
    m = DATE_IN_NAME.search(Path(path).name)
    if not m:
        raise ValueError(f"파일 이름에 받은 날짜(_YYYY-MM-DD.csv)가 없음: {path}")
    return dt.date.fromisoformat(m.group(1))


# ---------------------------------------------------------------- 파서

def read_trends_csv(path) -> pd.DataFrame:
    """Trends CSV(수동 다운로드·이 모듈 저장본 공통)를 읽는다.

    반환: 컬럼 week(YYYY-MM-DD) + 키워드(소문자)들. 값은 원본 문자열 그대로("<1" 포함).
    """
    text = Path(path).read_text(encoding="utf-8-sig")
    lines = text.splitlines()
    header_idx = None
    for i, line in enumerate(lines):
        cells = next(csv.reader([line]), [])
        if cells and cells[0].strip().lower() in TIME_HEADERS and len(cells) > 1:
            header_idx = i
            break
    if header_idx is None:
        raise ValueError(f"헤더 줄(Week,...)을 찾지 못함: {path}")

    df = pd.read_csv(io.StringIO("\n".join(lines[header_idx:])),
                     dtype=str, keep_default_na=False)
    time_col = df.columns[0]
    if time_col.strip().lower() not in ("week", "time", "date"):
        raise ValueError(f"주 단위 파일이 아님 ({time_col}): {path}")

    # "toilet paper: (United States)" -> "toilet paper"
    rename = {time_col: "week"}
    for c in df.columns[1:]:
        rename[c] = re.sub(r":\s*\(.*\)\s*$", "", c).strip().lower()
    df = df.rename(columns=rename)
    df = df[[c for c in df.columns if c != "ispartial"]]

    weeks = pd.to_datetime(df["week"].str.strip())
    if not (weeks.dt.dayofweek == 6).all():
        bad = df.loc[weeks.dt.dayofweek != 6, "week"].head(3).tolist()
        raise ValueError(f"주 시작이 일요일이 아닌 날짜가 있음 {bad}: {path}")
    df["week"] = weeks.dt.strftime("%Y-%m-%d")
    for c in df.columns[1:]:
        df[c] = df[c].str.strip()
    return df


def write_trends_csv(df: pd.DataFrame, path: Path) -> None:
    """수동 다운로드와 같은 형식으로 저장한다."""
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write("Category: All categories\n\n")
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["Week"] + [f"{k}: ({GEO_LABEL})" for k in df.columns[1:]])
        w.writerows(df.itertuples(index=False, name=None))


# ---------------------------------------------------------------- 수집

def _timeline_to_frame(timeline: list[dict], keywords: list[str]) -> pd.DataFrame:
    rows = []
    for point in timeline:
        week = dt.datetime.fromtimestamp(int(point["time"]), dt.timezone.utc).date()
        values = point["formattedValue"]
        if len(values) != len(keywords):
            raise ValueError("응답의 값 개수가 키워드 수와 다름")
        rows.append([week.isoformat()] + [str(v) for v in values])
    return pd.DataFrame(rows, columns=["week"] + keywords)


def fetch_bundle(keywords: list[str]) -> pd.DataFrame:
    """한 묶음을 받는다. 차단(429)·오류 시 지수 대기 후 새 세션으로 재시도."""
    import requests
    from pytrends import exceptions as pt_exc
    from pytrends.request import TrendReq

    retryable = (pt_exc.TooManyRequestsError, pt_exc.ResponseError,
                 requests.exceptions.RequestException, ValueError, KeyError)
    for attempt in range(MAX_RETRIES + 1):
        try:
            # tz=0: 주 시작 시각을 UTC 자정으로 받아 날짜가 밀리지 않게 한다
            client = TrendReq(hl="en-US", tz=0, timeout=(10, 30))
            client.build_payload(keywords, cat=CATEGORY, timeframe=TIMEFRAME,
                                 geo=GEO, gprop=GPROP)
            widget = client.interest_over_time_widget
            data = client._get_data(
                url=TrendReq.INTEREST_OVER_TIME_URL,
                method=TrendReq.GET_METHOD,
                trim_chars=5,
                params={"req": json.dumps(widget["request"]),
                        "token": widget["token"], "tz": client.tz},
            )
            df = _timeline_to_frame(data["default"]["timelineData"], keywords)
            if df.empty:
                raise ValueError("빈 응답")
            return df
        except retryable as e:
            if attempt == MAX_RETRIES:
                raise
            wait = min(BASE_WAIT * 2 ** attempt, MAX_WAIT) * random.uniform(0.8, 1.2)
            print(f"  [{attempt + 1}/{MAX_RETRIES}] {type(e).__name__}: {e} "
                  f"-> {wait:.0f}초 대기 후 재시도")
            time.sleep(wait)
    raise RuntimeError("unreachable")


def collect(bundles: list[int], raw_dir: Path = RAW_DIR,
            fetched: dt.date | None = None) -> list[Path]:
    fetched = fetched or dt.date.today()
    raw_dir.mkdir(parents=True, exist_ok=True)
    saved = []
    for n, b in enumerate(bundles):
        keywords = bundle_keywords(b)
        path = raw_dir / raw_filename(keywords, fetched)
        if path.exists():
            print(f"묶음 {b}: 이미 있음, 건너뜀 ({path.name})")
            continue
        if n > 0:
            time.sleep(random.uniform(*BETWEEN_BUNDLES))
        print(f"묶음 {b}: {keywords} 받는 중")
        df = fetch_bundle(keywords)
        write_trends_csv(df, path)
        print(f"  저장 {path.name} ({len(df)}주, {df['week'].iloc[0]} ~ {df['week'].iloc[-1]})")
        saved.append(path)
    return saved


def import_manual(src: Path, fetched: dt.date, raw_dir: Path = RAW_DIR) -> Path:
    """수동 다운로드 CSV를 검사한 뒤 규칙에 맞는 이름으로 그대로 복사한다."""
    df = read_trends_csv(src)
    b = identify_bundle(df.columns[1:])
    dest = raw_dir / raw_filename(bundle_keywords(b), fetched)
    if dest.exists():
        raise FileExistsError(f"이미 있음: {dest}")
    raw_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)
    print(f"묶음 {b}: {src} -> {dest.name} ({len(df)}주)")
    return dest


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--bundles", type=int, nargs="+", choices=sorted(BUNDLES),
                   default=sorted(BUNDLES))
    p.add_argument("--import", dest="import_path", type=Path,
                   help="수동으로 내려받은 CSV 경로")
    p.add_argument("--date", type=dt.date.fromisoformat,
                   help="받은 날짜 (기본: 오늘)")
    p.add_argument("--raw-dir", type=Path, default=RAW_DIR)
    args = p.parse_args()

    if args.import_path:
        import_manual(args.import_path, args.date or dt.date.today(), args.raw_dir)
    else:
        collect(args.bundles, args.raw_dir, args.date)


if __name__ == "__main__":
    main()
