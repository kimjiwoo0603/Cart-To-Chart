# Cart-To-Chart
이화여자대학교 빅데이터시각화 수업의 Cart To Chart 팀 프로젝트 저장소입니다.

## 연구 질문
유행(Google 검색량 급증)과 Amazon에서의 실제 구매, 그리고 구매 후 남기는 리뷰는 어떤 관계가 있는가?

## 데이터셋
| # | 데이터 | 유형 | 출처 | 저장 위치 |
|---|---|---|---|---|
| 1 | Google Trends | 시계열 | https://trends.google.com/explore | `data/raw/google_trends/` |
| 2 | Open E-commerce 1.0 (Amazon 구매 이력) | 표 형식 | https://www.media.mit.edu/projects/crowdsourcing-purchase-histories/overview/ | `data/raw/open_ecommerce/` |
| 3 | Amazon Reviews 2023 (빅데이터) | 텍스트 | https://amazon-reviews-2023.github.io/ | `data/raw/amazon_reviews/` |

2번과 3번은 상품 ID인 **ASIN**으로 조인합니다.

## 원본 데이터 받기
원본 데이터는 용량이 커서 git에 올리지 않습니다 (GitHub는 100MB가 넘는 파일을 받지 않음). 각자 아래 링크에서 받아 표의 위치에 파일 이름 그대로 저장하세요.

| 데이터 | 파일 | 크기 | 받는 곳 | 저장 위치 |
|---|---|---|---|---|
| Open E-commerce 1.0 | `amazon-purchases.csv` | 313MB | [Harvard Dataverse](https://doi.org/10.7910/DVN/YGLYDY) ([바로 받기](https://dataverse.harvard.edu/api/access/datafile/7616235?format=original)) | `data/raw/open_ecommerce/` |
| Amazon Reviews 2023 (Home and Kitchen) | `Home_and_Kitchen.jsonl.gz` | 8.3GB (압축) | [McAuley Lab](https://amazon-reviews-2023.github.io/) ([바로 받기](https://mcauleylab.ucsd.edu/public_datasets/data/amazon_2023/raw/review_categories/Home_and_Kitchen.jsonl.gz)) | `data/raw/amazon_reviews/` |
| Google Trends | 검색어별 CSV | - | [Google Trends](https://trends.google.com/explore)에서 직접 내려받기 | `data/raw/google_trends/` |

- Amazon Reviews는 카테고리마다 파일이 따로 있습니다. 다른 카테고리가 필요하면 위 주소의 `Home_and_Kitchen` 부분을 카테고리 이름으로 바꾸면 됩니다.
- 리뷰 파일은 압축을 풀면 훨씬 커지므로 `.gz` 그대로 두고 읽는 것을 권장합니다.
- 터미널에서 받을 때:
  ```bash
  curl -L -o data/raw/open_ecommerce/amazon-purchases.csv "https://dataverse.harvard.edu/api/access/datafile/7616235?format=original"
  curl -L -C - -o data/raw/amazon_reviews/Home_and_Kitchen.jsonl.gz "https://mcauleylab.ucsd.edu/public_datasets/data/amazon_2023/raw/review_categories/Home_and_Kitchen.jsonl.gz"
  ```
  (`-C -`는 받다가 끊기면 이어받기)

## 폴더 구조
```
Cart-To-Chart/
├── data/                        # 데이터 파일은 git에 올리지 않음 (.gitignore)
│   ├── raw/                     # 원본 그대로
│   │   ├── google_trends/
│   │   ├── open_ecommerce/
│   │   └── amazon_reviews/
│   ├── interim/                 # 정제 중간 결과
│   │   ├── cleaned_trends/
│   │   ├── cleaned_purchase/
│   │   └── filtered_reviews/
│   └── processed/               # 분석에 바로 쓰는 주간 데이터
│       ├── weekly_trends/
│       ├── weekly_purchase/
│       ├── weekly_reviews/
│       └── integrated/
├── mapping/
│   └── keyword_product_mapping.csv   # 키워드–상품 매핑 (논문팀·전처리팀 공유)
├── logs/
│   └── preprocessing_log.md     # 전처리 결정 기록
├── src/
│   ├── collect/                 # 데이터 수집·다운로드
│   ├── preprocess/              # 정제 및 ASIN 조인
│   └── eda/
├── notebooks/
├── analysis/
│   ├── eda/                     # EDA 그래프
│   └── lag_analysis/
├── docs/literature/             # 선행논문 정리
└── presentation/
    ├── slides/
    └── video/
```

## 브랜치
조원별 브랜치에서 작업하고 PR로 `main`에 합칩니다.

| 조원 | 브랜치 |
|---|---|
| 김지우 | `kimjiwoo` |
| 김다빈 | `kimdabin` |
| 정세은 | `jeongseeun` |
| 남지원 | `namjiwon` |
| 안서연 | `anseoyeon` |

## 시작하기
```bash
pip install -r requirements.txt
```
