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
├── data/                  # 데이터는 git에 올리지 않음 (.gitignore)
│   ├── raw/               # 원본 그대로 (데이터셋별 하위 폴더)
│   ├── interim/           # 정제 중간 결과
│   └── processed/         # 분석/시각화에 바로 쓰는 최종 데이터
├── src/
│   ├── collect/           # 데이터 수집·다운로드 스크립트
│   ├── preprocess/        # 정제 및 ASIN 조인
│   └── eda/               # 탐색적 분석, 그래프 생성
├── notebooks/             # 실험용 주피터 노트북
├── reports/figures/       # 발표에 쓸 그래프 이미지
└── docs/
    ├── literature/        # 선행논문 조사
    └── slides/            # 발표 자료
```

## 시작하기
```bash
pip install -r requirements.txt
```
