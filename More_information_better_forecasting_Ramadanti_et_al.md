# Ramadanti et al. (2026) — More information, better forecasting?

## 1. 논문 정보
- **Title:** More information, better forecasting? Empirical evidence from integrating customer sentiment and Google Trends
- **Authors:** Ristanti Ramadanti, Vasileios Bougioukos, Konstantinos Nikolopoulos
- **Journal:** International Journal of Production Research
- **Year:** 2026
- **DOI:** 10.1080/00207543.2026.2688940
- **분류:** `[RQ1]` `[RQ2]` `[METHOD]`
- **선정 이유:** Google Trends 검색 데이터와 Amazon 고객 리뷰 데이터를 실제 판매량과 결합하여 분석했다는 점에서 우리 연구와 사용하는 데이터 및 분석 구조가 유사함
---

## 2. 연구 목적
본 연구의 핵심 목적은 **Google Trends의 검색 관심도와 Amazon 고객 리뷰에서 추출한 추가 정보가 제품 판매량 예측 성능을 향상시키는지** 확인하는 것이다.
특히 다음을 검토한다.

1. Amazon 리뷰의 감성을 추출할 때 VADER와 TextBlob 중 어떤 도구가 더 적절한가?
2. Google Trends와 고객 리뷰 관련 변수를 추가하면 판매량 예측 성능이 향상되는가?
3. 검색 및 리뷰 정보와 실제 판매 사이에 시간적 지연(time lag)이 존재하는가?
4. 이러한 추가 정보는 선형 모델보다 비선형 모델에서 더 효과적으로 활용되는가?
본 연구는 특정 예측 알고리즘의 우열 자체보다는 **검색 및 리뷰라는 추가적인 소비자 정보를 판매 예측에 포함하는 것이 실제로 도움이 되는지**에 초점을 둔다.
---

## 3. 데이터

본 연구는 크게 세 종류의 데이터를 결합하였다.

### ① Google Trends

- 게임 콘솔 제품별 검색 키워드의 상대적 검색 관심도(relative search popularity)
- Google Trends API를 통해 수집
- Google Trends 데이터는 실제 검색 횟수가 아니라 상대적 검색 인기도를 의미함
- 월별 데이터를 수집한 후 분기별 평균값으로 집계
- 제품 간 비교를 위해 `Console`을 reference keyword로 사용

### ② Amazon Reviews

- Amazon.com 미국 marketplace의 제품 리뷰
- 기간: 2000–2018
- Electronics 및 Video Games 카테고리
- 전체 데이터셋은 2,300만 개 이상의 리뷰를 포함
- 연구에서는 12개 게임 콘솔 제품을 중심으로 약 130만 개 이상의 리뷰를 활용
- 28,000개 이상의 unique product ID 중 579개가 console product에 해당

주요 리뷰 정보:
- Review text
- Review summary
- Star rating
- Helpful votes
- Review count

### ③ Sales

Nintendo, Sony PlayStation, Microsoft Xbox의 게임 콘솔 판매량을 사용하였다.

판매량은 주로 다음 자료에서 수집하였다.

- 기업 재무보고서
- Investor Relations 자료
- 기업 공식 웹사이트
- 기업 발표 자료
- 일부 third-party 자료 및 뉴스

최종적으로 12개 게임 콘솔 제품을 분석하였다.

- Nintendo Switch
- Nintendo 2DS
- Nintendo Wii U
- Nintendo 3DS
- Nintendo Wii
- Nintendo DS
- PlayStation 4
- PlayStation 3
- PlayStation Portable
- PlayStation 2
- Xbox One
- Xbox 360

---

## 4. 데이터 처리

전체 분석 과정은 다음 네 단계로 구성된다.

1. Data preparation
2. Sentiment analysis
3. Variable aggregation / Feature engineering
4. Predictive analysis

Google Trends, Amazon Reviews, Sales 데이터를 동일한 **분기(quarter)** 단위로 맞춘 후 분석하였다.

---

## 5. 리뷰 감성 분석

Amazon 리뷰 텍스트의 감성을 분석하기 위해 두 가지 Sentiment Extraction Tool(SET)을 비교하였다.

### TextBlob

다음 값을 생성한다.

- Polarity
- Subjectivity

Polarity는 -1~1 범위이며,

- -1: negative
- +1: positive

를 의미한다.

### VADER

다음 값을 생성한다.

- Positivity
- Negativity
- Neutrality
- Compound score

Compound score는 -1~1 범위로 전체적인 감성의 방향과 강도를 나타낸다.

### 감성 분석 검증

Amazon의 실제 star rating을 감성의 ground truth에 대한 proxy로 사용하였다.

- 1~3 stars → Negative
- 4~5 stars → Positive

이후 Accuracy, Precision, Recall, F1 Score를 이용하여 TextBlob과 VADER의 성능을 비교하였다.

### 결과

게임 콘솔 Amazon 리뷰에서는 **VADER가 TextBlob보다 더 적절한 sentiment extraction tool로 나타났다.**

따라서 우리 연구에서 Amazon 리뷰의 감성을 분석할 경우 **VADER를 우선적인 baseline 방법으로 고려할 근거**가 된다.

---

## 6. 리뷰 관련 변수 생성

연구에서는 단순 평균 감성뿐 아니라 다양한 리뷰 관련 변수를 생성하였다.

예:

- Review count
- Average sentiment score
- Cumulative average sentiment
- Positive-to-Negative Ratio (PNR)
- Relative review count
- Star rating
- Helpful votes
- Review summary sentiment

특히 PNR은 일정 기간 동안의 positive review와 negative review의 비율을 나타낸다.

이 연구는 단순히 리뷰 수만 사용하는 것보다 **리뷰 volume + sentiment를 함께 고려**한다는 특징이 있다.

---

# 7. Time Lag 분석

이 논문에서 우리 연구에 가장 직접적으로 참고할 수 있는 부분이다.

저자들은 Google Trends 및 customer review 관련 변수의 현재 값으로 판매량을 예측할 경우 실제 forecasting이 아니라 현재 시점의 정보를 사용하는 문제가 발생할 수 있다고 보고 **time lag를 적용하였다.**

### Cross-correlation Analysis

검색량 및 리뷰 관련 변수와 판매량 사이의 적절한 시차를 찾기 위해 **Cross-correlation analysis**를 사용하였다.

분석 범위:

- Minimum lag: 1 quarter
- Maximum lag: 4 quarters

각 변수에 대해 판매량과의 **상관관계 절댓값이 가장 강한 lag를 선택**하였다.

또한 제품마다 소비자 행동이 다를 수 있다고 보고 **제품별로 별도의 optimal lag를 계산하였다.**

### 주요 결과

제품별로 검색량 및 리뷰 변수와 판매량 사이의 optimal lag가 서로 다르게 나타났다.

대부분의 제품에서 Google Trends 검색 관심도와 판매량의 가장 강한 상관은 비교적 긴 lag에서 나타났다.

특히 PlayStation Portable을 제외한 제품에서 Google Trends 검색 관심도가 판매량과 가장 강한 상관을 보이는 lag가 **4 quarters**였다.

그러나 저자들은 이를 그대로 소비자 행동에 따른 시차라고 해석하지 않았다.

게임 콘솔 판매 자체에 강한 **4-quarter seasonal cycle**이 존재했기 때문에, 관찰된 lag가 실제 소비자의 검색 → 구매 과정 때문인지 계절성 때문인지 명확히 구분하기 어렵기 때문이다.

따라서 저자들은 de-seasonalised data를 이용한 추가 분석이 필요하다고 지적하였다.

---

# 8. 분석 방법

연구에서 사용한 주요 통계 및 분석 방법은 다음과 같다.

### Pearson Correlation

Google Trends, 리뷰 관련 변수와 판매량 사이의 관계를 확인하고 변수 선택에 사용하였다.

### Variance Inflation Factor (VIF)

다중공선성을 확인하고 VIF가 높은 변수를 제거하였다.

### Cross-correlation Analysis

Google Trends 및 리뷰 관련 변수와 판매량 사이의 적절한 time lag를 결정하였다.

### Granger Causality Test

검색 관심도 및 리뷰 감성의 과거 값이 이후 판매량을 예측하는 데 유의한 정보를 제공하는지 검정하였다.

### Forecasting Models

다음 선형 및 비선형 모델을 비교하였다.

- Multiple Time-Series Linear Regression
- Decision Tree Regression
- Random Forest
- Gradient Boosting
- Support Vector Regression (SVR)

### 평가 지표

- Adjusted R²
- RMSE

또한 80% / 20% split을 이용하여 out-of-sample forecasting을 수행하였다.

---

# 9. 주요 결과

## ① Google Trends는 판매량과 관련이 있음

Google Trends의 relative search popularity는 대부분의 제품에서 판매량과 양의 상관관계를 보였다.

제품별 분석에서는 Google Trends가 다른 여러 변수보다 판매량과 강한 관계를 보이는 경우가 많았다.

따라서 검색 관심도는 소비자의 제품 관심을 나타내는 지표이자 이후 실제 수요를 설명하는 변수로 활용될 가능성이 있다.

---

## ② 검색 및 리뷰 정보에는 Time Lag가 존재함

Google Trends와 Amazon 리뷰 관련 변수의 과거 값이 판매량과 유의한 관계를 보였으며, optimal lag는 제품별로 다르게 나타났다.

따라서 검색량과 구매/판매량 사이의 관계를 분석할 때 **동일 시점의 단순 상관관계만 보는 것보다 lag를 고려하는 것이 중요하다.**

---

## ③ Google Trends + Reviews를 추가하면 예측력이 전반적으로 향상됨

Google Trends와 customer review 변수를 포함한 전체 product sales model의 R²는 **42.8%**였으며, 추가 정보를 포함하지 않은 모델보다 R²가 **44.6% 증가**하였다.

전체적인 예측 error 역시 감소하였다.

Company-level sales forecasting에서도 Google Trends와 리뷰 정보를 포함한 모델의 R²는 **61.8%**로 나타났다.

다만 모든 제품에서 성능이 향상된 것은 아니며 일부 제품에서는 추가 변수를 넣었을 때 overfitting이 발생하였다.

따라서 검색과 리뷰 정보를 추가한다고 해서 **항상** 예측 성능이 향상된다고 볼 수는 없다.

---

## ④ 비선형 관계의 가능성

전체 company sales의 out-of-sample forecasting에서는 **Random Forest**가 가장 좋은 성능을 보였다.

제품별로 가장 적합한 알고리즘은 서로 달랐지만 전반적으로 비선형 모델이 좋은 성능을 보이는 경우가 많았다.

이는 검색량, 리뷰 및 판매량 사이의 관계가 단순한 선형 관계만으로 설명되지 않을 가능성을 보여준다.

---

# 10. 논문의 한계

### ① 시간 단위가 너무 큼

판매 데이터가 분기별로 제공되기 때문에 Google Trends와 Amazon Reviews 데이터 역시 **quarter 단위로 집계**하였다.

따라서 검색과 판매 사이의 세밀한 시간적 관계를 파악하기 어렵다.

저자들도 향후 연구에서는 **weekly 또는 monthly sales data**를 이용할 필요가 있다고 제안하였다.

### ② 계절성 문제

게임 콘솔 판매에는 강한 계절성이 존재한다.

특히 4-quarter lag에서 강한 관계가 나타난 것이 실제 검색 → 구매 행동의 시차인지 연간 계절성 때문인지 명확하게 구분하기 어렵다.

따라서 de-seasonalisation이 필요하다.

### ③ 데이터의 공간적 범위가 일치하지 않음

Amazon 리뷰는 주로 미국 marketplace 데이터이지만 판매량은 global sales를 사용하였다.

따라서 리뷰와 판매 데이터가 대표하는 시장 범위가 완전히 일치하지 않는다.

### ④ 판매 데이터 출처의 이질성

Nintendo를 제외한 일부 제품의 판매량은 기업 보고서뿐 아니라 third-party 자료, 뉴스, 블로그 및 기업 발표 자료 등 여러 출처에서 수집하였다.

따라서 판매 데이터의 신뢰성과 일관성에 한계가 있다.

### ⑤ 감성 분류의 단순화

감성을 Positive / Negative 두 범주로 단순화하였으며 Neutral class를 별도로 구성하지 않았다.

따라서 sentiment classification의 정확도 평가는 제한적인 proxy에 해당한다.

---

# 11. 우리 프로젝트와의 연결

우리 프로젝트:

> **관심(검색) → 행동(구매) → 평가(리뷰)**

본 논문:

> **Google Trends + Amazon Reviews → Sales forecasting**

따라서 사용하는 데이터의 종류는 매우 유사하지만, 데이터 사이의 관계를 설정하는 방식이 다르다.

---

## 📈 검색 → 구매

**관련성: 매우 높음**

본 논문은 Google Trends의 상대적 검색 관심도와 실제 판매량 사이의 관계를 분석하고, 특히 **Cross-correlation을 이용해 optimal time lag를 계산하였다.**

이는 우리 RQ1과 직접적으로 연결된다.

### 우리 RQ1

> **검색량 급증 후 구매량은 몇 주의 시차를 두고 증가하는가?**

논문:

`Google Trends(t-lag) → Sales(t)`

우리 연구:

`Google Trends(t-lag) → Actual Purchase(t)`

### 참고할 분석 방법

- Cross-correlation
- Product별 lag 계산
- 검색량과 구매량의 Pearson correlation
- 시계열 계절성 확인
- spike 처리
- 제품별 차이 확인

특히 논문에서 **제품마다 optimal lag가 다르게 나타났다는 점**은 우리 연구에서도 모든 상품을 하나로 합쳐 하나의 lag를 설정하기보다 product type별 lag를 확인해야 할 필요성을 보여준다.

---

## 🛒 구매 → 리뷰

**관련성: 부분적으로 관련**

본 논문은 Amazon 리뷰의

- Review count
- Star rating
- Sentiment
- Helpful votes
- PNR

등을 활용한다.

따라서 우리 RQ2에서 사용할 **리뷰 변수의 구성 방식과 sentiment analysis 방법**을 참고할 수 있다.

### 우리 RQ2

> **검색량 급증 시기 이후 리뷰 수와 평점 및 감성은 어떻게 변하는가?**

특히 다음 변수를 참고할 수 있다.

- 리뷰 수
- 평균 star rating
- 평균 sentiment score
- Positive-to-Negative Ratio
- VADER compound score

다만 중요한 차이가 있다.

본 논문은 주로 **과거 리뷰 정보가 이후 판매량을 얼마나 잘 예측하는가**를 분석한다.

반면 우리 연구에서는

`검색 spike → 구매 증가 → 이후 리뷰 변화`

를 분석한다.

즉 리뷰의 시간적 위치와 해석 방향이 다르다.

---

## 🔄 유행 → 구매 → 리뷰

**관련성: 높지만 구조는 다름**

본 논문은 Google Trends, Amazon Reviews, Sales의 세 종류 데이터를 하나의 분석에 포함한다.

그러나 세 데이터를

> 검색 → 구매 → 리뷰

라는 순차적 소비자 행동 과정으로 직접 연결하지는 않는다.

Google Trends와 Amazon Reviews를 모두 **판매량을 예측하기 위한 독립변수**로 사용한다.

즉 논문의 기본 구조는

`Google Trends ─┐`
`               ├→ Sales`
`Amazon Reviews ─┘`

이다.

반면 우리 연구의 구조는

`Google Trends → Purchase → Review`

이다.

이 차이가 우리 연구의 핵심적인 차별점이다.

---

# 12. RQ별 활용

## RQ1
> 검색량 급증 후 구매량은 몇 주의 시차를 두고 증가하는가?

### 직접 참고 가능

- Cross-correlation을 이용한 lag 탐색
- 상품별 optimal lag 계산
- Google Trends와 실제 소비 행동 데이터의 시간축 정렬
- 계절성이 lag를 왜곡할 가능성 확인
- 제품별 lag 차이 확인

특히 본 논문은 1~4 quarter 범위에서 lag를 탐색했지만, 우리 연구에서는 더 세밀한 실제 구매 날짜가 존재하므로 **week 단위 lag 분석**으로 확장할 수 있다.

---

## RQ2
> 검색량 급증 시기 이후 리뷰 수와 평점 및 감성은 어떻게 변하는가?

### 직접/부분 참고 가능

논문에서 사용한 다음 리뷰 지표를 활용할 수 있다.

- Review count
- Average star rating
- VADER compound score
- Positive / Negative sentiment
- PNR

특히 VADER와 TextBlob을 실제 star rating과 비교한 결과 VADER가 더 적절하게 나타났으므로, 우리 연구의 sentiment analysis 방법을 결정할 때 참고할 수 있다.

다만 본 논문은 검색 spike 전후의 리뷰 변화를 직접 비교하지 않았으므로 **spike 전/후 비교는 우리 연구에서 추가해야 한다.**

---

## RQ3
> 유행 상품과 꾸준히 팔리는 상품은 구매 후 평가 패턴이 다른가?

### 간접 참고 가능

본 논문에서도 제품마다

- 검색량과 판매량의 관계
- optimal lag
- 중요한 review variable
- 가장 적합한 forecasting model

이 서로 다르게 나타났다.

따라서 상품별 소비자 반응이 동일하지 않다는 점은 RQ3의 필요성을 뒷받침한다.

다만 본 논문에서는 상품을 **유행 상품 vs 꾸준히 팔리는 상품**으로 분류하여 비교하지 않았다.

따라서 유행성 분류 기준과 두 그룹 간 구매·평가 패턴 비교는 우리 연구에서 새롭게 정의해야 한다.

---

# 13. 우리 연구에 참고할 점

1. **Google Trends와 실제 소비 행동 사이의 lag 분석에 Cross-correlation을 활용할 수 있다.**
2. 하나의 공통 lag보다 **상품별 optimal lag를 확인하는 것이 필요하다.**
3. 계절성이 Cross-correlation 결과를 왜곡할 수 있으므로 구매량과 검색량의 seasonality를 먼저 확인해야 한다.
4. Google Trends의 spike가 반드시 동일한 규모의 구매 증가로 이어지는 것은 아니므로 spike 자체를 별도로 분석할 필요가 있다.
5. Amazon 리뷰 분석에는 Review count, Star rating, Sentiment, PNR 등을 활용할 수 있다.
6. 감성 분석의 baseline으로 **VADER**를 우선 고려할 수 있다.
7. 검색량·리뷰·구매 사이에 비선형 관계가 존재할 가능성도 고려해야 한다.
8. 분기별 데이터보다 세밀한 **주별 데이터**를 활용하면 검색 → 구매의 시차를 더 구체적으로 분석할 수 있다.

---

# 14. 우리 연구와 다른 점

본 논문과 우리 연구는 Google Trends, Amazon 관련 소비자 데이터, 리뷰 데이터를 함께 사용한다는 점에서 매우 유사하다.

그러나 연구의 목적과 데이터 연결 구조에는 중요한 차이가 있다.

### 기존 연구

> **Google Trends + Amazon Reviews → Sales Forecasting**

검색량과 리뷰 정보를 판매량을 예측하기 위한 predictor로 사용한다.

### 우리 연구

> **관심(Search) → 행동(Purchase) → 평가(Review)**

검색, 실제 구매, 구매 후 평가를 **순차적인 소비자 행동 과정**으로 연결한다.

또한 본 논문은 기업이 보고한 aggregate sales를 사용하지만, 우리 연구에서는 Open e-commerce 1.0의 **개인 단위 실제 Amazon 구매 기록**을 활용한다.

따라서 우리 연구는 단순히 판매량 예측 정확도를 높이는 것이 아니라,

- 검색 관심의 증가가 실제 구매로 이어지는 데 얼마나 시간이 걸리는지
- 구매 증가 이후 소비자의 평가가 어떻게 변화하는지
- 이러한 과정이 유행 상품과 꾸준한 상품에서 다르게 나타나는지

를 분석한다는 점에서 차이가 있다.
---
