# Google Trends 전처리 점검 결과

`python -m src.preprocess.trends` 실행 시 자동 생성 (2026-10-04 22:39). 결정 사항은 `preprocessing_log.md` 참고.

## 입력 파일
| bundle | run | run_date | file | missing_weeks | extra_weeks |
|---|---|---|---|---|---|
| 1 | 1 | 2026-10-04 | blanket+toilet-paper+disinfecting-wipes+jigsaw-puzzle+baking-pan_2026-10-04.csv | 0 | 0 |
| 2 | 1 | 2026-10-04 | blanket+baking+weighted-blanket+tumbler_2026-10-04.csv | 0 | 0 |
| 3 | 1 | 2026-10-04 | blanket+air-purifier+air-fryer_2026-10-04.csv | 0 | 0 |

## 결측 주 (0으로 채우지 않고 결측으로 둠)
(없음)

## 정규화 기준(100) 위치
회차마다 100이 된 키워드·주가 바뀐 묶음은 회차별로 스케일이 다르다는 뜻이고, 회차별 환산 후 평균하는 근거가 된다.

| bundle | run | run_date | peak | peak_changed_in_bundle |
|---|---|---|---|---|
| 1 | 1 | 2026-10-04 | toilet paper @ 2020-03-15 | False |
| 2 | 1 | 2026-10-04 | blanket @ 2020-12-06 | False |
| 3 | 1 | 2026-10-04 | air fryer @ 2020-12-27 | False |

## 환산 계수와 주별 비율 분포
`factor` = sum(묶음 1 blanket) / sum(이 묶음 blanket), 같은 회차끼리. `ratio_*`는 주별 비율(묶음 1 blanket_t / 이 묶음 blanket_t)의 분포. CV가 작고 min~max가 좁으면 상수 하나로 환산해도 된다는 근거다.

| bundle | run | run_date | ref_date | factor | ratio_mean | ratio_median | ratio_cv | ratio_min | ratio_max | n_weeks |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 1 | 2026-10-04 | 2026-10-04 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 1.0000 | 1.0000 | 261 |
| 2 | 1 | 2026-10-04 | 2026-10-04 | 0.3310 | 0.3307 | 0.3333 | 0.0235 | 0.3103 | 0.3448 | 261 |
| 3 | 1 | 2026-10-04 | 2026-10-04 | 0.5167 | 0.5163 | 0.5185 | 0.0260 | 0.5000 | 0.5556 | 261 |

## 회차 간 차이 > 20 (원본 스케일)
(없음)

## 키워드별 평균에 쓴 회차 수
| keyword | min | max |
|---|---|---|
| air fryer | 1 | 1 |
| air purifier | 1 | 1 |
| baking | 1 | 1 |
| baking pan | 1 | 1 |
| blanket | 1 | 1 |
| disinfecting wipes | 1 | 1 |
| jigsaw puzzle | 1 | 1 |
| toilet paper | 1 | 1 |
| tumbler | 1 | 1 |
| weighted blanket | 1 | 1 |

## 출력
- weekly_trends.csv: 1566행, 품목 6개, 주 261개 (2017-12-31 ~ 2022-12-25)
- spikes.csv: 31건

### 품목별 spike 수 (RQ3 유행형/꾸준형 분류용)
| product_type | trends | trends_yoy |
|---|---|---|
| TOILET_PAPER | 4 | 2 |
| SURFACE_CLEANING_WIPE | 1 | 1 |
| PUZZLES | 0 | 0 |
| BAKING_PAN | 6 | 3 |
| BLANKET | 5 | 3 |
| DRINKING_CUP | 4 | 2 |
