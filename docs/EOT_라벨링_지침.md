# EOT 라벨링 지침 (화장지 시험 분석, 2026-10-06)

출처: Attri et al. (2025), *Why We Feel What We Feel*, Findings of EMNLP 2025, **부록 D "Annotation Guidelines"** (pp.5528–5530)와 본문 3장·5.1절.
논문 지침을 한국어로 옮기고, 논문에 없는 부분(감정별 설명, 화장지 예시, 시트 작성법, 우리 팀 판단 규칙)은 **[우리 추가]** 로 표시했다.
사람 라벨러 2명과 모델(Mistral-7B)이 **같은 기준**을 쓰도록, 모델 프롬프트(05 노트북)도 이 지침의 논문 부분으로 만들었다. [우리 추가] 판단 규칙은 논문 재현을 위해 프롬프트에 넣지 않았다.

**라벨러 (10/6 지우 확정)**: 정세은 = `label_sheet_A.csv`, 김다빈 = `label_sheet_B.csv`. 지침 2장 판단 규칙도 10/6 확정.

---

## 1. 과제 (D.1)
리뷰 하나를 읽고 두 가지를 한다.
1. **감정 찾기**: 리뷰에 드러난 감정을 Plutchik 8개 기본 감정에서 **모두** 고른다.
2. **원인 구절(Opinion Trigger) 뽑기**: 고른 감정마다, **왜 그 감정이 생겼는지 설명하는 구절**을 리뷰 본문에서 그대로 복사한다.

## 2. 감정 9개 (D.2, 3.1절)
아래 8개만 쓴다. 하나도 없으면 **Neutral**(중립).

| 감정 | 뜻 [우리 추가] | 화장지 리뷰에서 나올 법한 표현 [우리 추가, 지어낸 예시] |
|---|---|---|
| Joy 기쁨 | 만족, 즐거움, 좋아함 | "love how soft it is", "so happy I found these" |
| Trust 신뢰 | 믿고 의지함, 품질·판매자·브랜드를 믿음, 꾸준히 삼 | "the only brand I buy", "always reliable", "will never switch" |
| Fear 두려움 | 불안, 걱정, 겁 | "worried we'd run out", "scared to go to the store" |
| Surprise 놀람 | 예상 밖이라 놀람 (좋든 나쁘든) | "was surprised how much came in the box", "didn't expect it to be this thin" |
| Sadness 슬픔 | 실망, 아쉬움, 서운함 | "very disappointed", "sad they changed the formula" |
| Disgust 혐오 | 역겨움, 질 낮은 것에 대한 거부감 | "feels like sandpaper", "smells awful", "gross" |
| Anger 분노 | 화남, 속았다는 느낌, 바가지 | "feel ripped off", "price gouging", "DO NOT BUY" |
| Anticipation 기대 | 앞으로의 일에 대한 기대·계획·준비 | "will buy again", "stocked up for the next month" |

**[우리 추가] 헷갈리는 쌍 판단 규칙** (논문 오류 분석 p.5522에서 모델이 자주 틀린 부분)
- **Joy vs Trust**: 품질에 만족하는 리뷰에서 가장 많이 헷갈린다. "좋다, 마음에 든다"는 **Joy**, "믿을 수 있다, 늘 이것만 산다, 추천한다"는 **Trust**. 둘 다 있으면 둘 다 표시한다.
- **Sadness vs Anger**: "disappointed"는 **Sadness**. 누군가의 잘못을 탓하거나 속았다고 하면("ripped off", "scam", "false advertising") **Anger**.
- **Disgust vs Anger**: 물건 자체가 불쾌하면(촉감·냄새) **Disgust**, 판매자·가격·광고에 화나면 **Anger**.
- **Fear vs Anticipation**: 걱정이면 **Fear**, 미래를 준비·기대하면 **Anticipation**. "사재기 때문에 못 살까 봐 미리 샀다"는 둘 다 가능하다.

## 3. 원인 구절(Trigger) 규칙 (D.3, 경계 사례)
trigger는 아래를 모두 만족해야 한다.
- **그대로 복사 (Extractive)**: 리뷰에 쓰인 글자 그대로. 고쳐 쓰기·요약·맞춤법 수정 금지. 대소문자·문장부호도 그대로.
- **감정과 직접 연결 (Clearly linked)**: 그 감정의 이유가 되는 부분.
- **혼자 읽어도 이해됨 (Self-contained)**: 앞뒤 문맥 없이도 뜻이 통하는 길이.

경계 사례
- **겹치는 구간**: 짧은 구간이 긴 구간 안에 들어 있으면, **가장 정보가 많고 자연스러운 구간** 하나를 고른다.
- **떨어진 구간 금지**: 문장 두 곳을 이어 붙이지 않는다. 가장 대표적인 **연속 구간** 하나를 고른다.
- **비교 표현**: "Better than all other brands I've tried"처럼 비교가 감정의 이유면 **비교 부분까지 전부** 넣는다.
- **감정 하나에 이유가 여러 개**면 trigger를 여러 개 적는다. 논문은 모델이 두 번째·세 번째 trigger를 자주 놓친다고 했다 (p.5522). 사람은 놓치지 않도록 한다.

## 4. 판단 원칙 (D.4, D.5)
- 리뷰 **전체를 끝까지 읽고** 시작한다.
- **여러 감정** 가능. 분명히 드러난 감정은 모두 표시한다.
- **강도는 보지 않는다.** 있다/없다만 판단한다.
- **분명히 드러난 감정만** 표시한다. 추측하지 않는다.
- 판단할 때는 **리뷰 전체 맥락**을 본다.
- **확신하는 것만** 표시한다.

## 5. 특수한 리뷰 (D.6)
- **아주 짧은 리뷰**: 감정이 분명하면 표시한다. 리뷰 전체가 trigger가 될 수 있다.
- **기술적인 리뷰** (매수, 겹 수, 크기 등): 수치 자체가 아니라 감정에 집중한다. 수치가 감정을 직접 일으켰을 때만 trigger로 넣는다 (예: "Only 143 sheets, not the 176 they claim" → Anger).
- **비꼬는 리뷰**: 글자 뜻이 아니라 **의도된 감정**을 표시하고, `memo` 칸에 "비꼼"이라고 적는다.

## 6. 시트 작성법 [우리 추가]
파일: `data/processed/eot_pilot/label_sheet_A.csv`(라벨러 A), `label_sheet_B.csv`(라벨러 B). 50건, 구간·평점은 숨겨져 있다.

| 열 | 작성 |
|---|---|
| `text` | 리뷰 본문. **절대 고치지 않는다** |
| `Joy` ~ `Anticipation` | 그 감정이 있으면 trigger를 `text`에서 **복사해 붙여 넣는다.** 여러 개면 ` \| `(공백-세로막대-공백)로 구분. 감정이 없으면 비워 둔다 |
| `Neutral` | 8개 감정 칸이 모두 비었으면 `1` |
| `memo` | 비꼼, 애매한 점 등 |

주의
- 엑셀에서 열면 **자동 고침**(따옴표 모양, 대문자 변환)이 trigger를 바꿀 수 있다. 직접 타이핑하지 말고 `text` 칸에서 **복사·붙여넣기**만 한다. Google 스프레드시트로 열어도 된다.
- **두 라벨러는 끝날 때까지 서로 상의하지 않는다.** 독립적으로 해야 일치도(κ)가 의미가 있다.
- 리뷰의 평점·시기를 찾아보지 않는다. 논문도 평점을 편향 때문에 뺐다 (p.5519).

## 7. 제출 전 자기 점검 (D.8 Quality Control)
- [ ] 감정 이름이 8개 + Neutral 안에 있다
- [ ] 모든 trigger가 본문에 **글자 그대로** 있다 (Ctrl+F로 찾아지면 OK)
- [ ] 감정과 trigger의 연결이 분명하다
- [ ] 분명한 감정 표현 중 빠뜨린 게 없다

## 8. 끝난 뒤: 일치도와 정답 만들기
- **일치도** (논문 5.1절): 감정은 감정별 있음/없음으로 κ를 계산한다. 논문은 3명이라 Fleiss κ를 썼고, 우리는 2명이라 **Cohen κ**를 주로 보고하고 비교용으로 Fleiss κ도 같이 계산한다. trigger는 **단어(토큰) 단위**로 겹치는 정도를 본다 ("very happy" vs "happy"도 부분 일치로 인정).
- **정답(gold) 만들기**: 두 사람이 다른 곳만 같이 보고 합의한다. trigger가 겹치면 논문처럼 **더 긴 구간**을 남긴다 (longest-span heuristic, p.5520).
- 이 정답과 모델 결과를 비교해 감정 P/R/F1, trigger ROUGE-L을 계산한다 (논문 Table 2·3 지표). 계산 코드는 다음 노트북에서 만든다.

## 9. 논문 출력 형식 (D.8) — 모델이 내는 형식, 시트와 1:1로 대응
```json
{
  "review_id": "123",
  "emotions": [
    {"emotion": "Joy", "triggers": ["works perfectly every time", "excellent battery life"]}
  ]
}
```
