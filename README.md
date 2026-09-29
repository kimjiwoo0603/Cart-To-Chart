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
