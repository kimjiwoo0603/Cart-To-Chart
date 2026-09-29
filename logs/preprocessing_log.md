# 전처리 로그

전처리 과정에서 내린 결정과 그 이유를 날짜순으로 기록합니다.

## 팀 통일 기준
| 항목 | 결정 | 날짜 |
|---|---|---|
| 기간 | 2018~2022 | |
| 지역 | 미국 | |
| 집계 단위 | 주 단위 | |
| 주 시작 요일 | TBD | |
| 날짜 형식 | TBD | |
| ASIN 컬럼명 | TBD | |
| Trends `<1` 처리 | TBD | |
| Spike 정의 | TBD | |

## 기록

### 2026-09-29 조인 가능성 테스트 준비 (김지우)
- Open E-commerce 컬럼명을 snake_case로 통일: `order_date`, `unit_price`, `quantity`, `state`, `title`, `asin`, `category`, `response_id`. 구매 금액은 `amount = unit_price × quantity`.
- 상품 코드는 `B0`로 시작하는 10자리는 ASIN, 숫자 9자리+숫자/X는 ISBN-10(도서)으로 분류해 `code_type` 컬럼에 기록.
- 기프트카드는 `category`에 GIFT_CARD가 있거나 제목에 "gift card"가 있으면 제거. 완전히 같은 행은 중복으로 보고 제거.
- 리뷰는 `asin`과 `parent_asin` 둘 다 구매 ASIN과 비교하고, 둘 중 하나라도 맞으면 남김.
- 리뷰 원본은 디스크에 저장하지 않고 스트리밍으로 읽으면서 매칭된 리뷰만 `data/interim/filtered_reviews/`에 저장.
