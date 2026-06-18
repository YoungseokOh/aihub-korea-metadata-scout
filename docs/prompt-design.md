# Prompt Design — K-Saju AI Reading System

> 차트→LLM 리딩 프롬프트 설계. MVP 구현 전 확정 기준.
> 작성: 2026-06-18. 상위 스펙: [mvp-global-ksaju.md](./mvp-global-ksaju.md).

## 아키텍처 한 줄

```
만세력 엔진 → 결정론 차트 JSON → LLM system prompt → 따뜻한 영어 리딩
```

LLM은 계산 안 함. 해석·톤·대화만 담당. 차트는 항상 JSON으로 전달 (환각 방지).

---

## 1. MVP에서 쓸 차트 필드 (6개)

| 필드 | 왜 필요한가 | 비고 |
|---|---|---|
| **Day Master** (일주 천간) | 정체성 훅 — "당신은 甲木(Yang Wood) 개척자". 모든 리딩의 기준점 | 필수 |
| **Day Master Strength** (일주 강약) | 성격 특성: strong=주도적·자기확신, weak=유연·타인의존 | 필수 |
| **Month Pillar** (월주) | Gen Z 현재 위치 — 커리어·부모기(17–32세). 직업·능력 질문과 직결 | 필수 |
| **Day Pillar** (일주 지지) | 자아(33–48세) — 인간관계·연애 리딩에 활용 | 필수 |
| **Elemental Balance** (오행 분포) | 구체성 핵심 — "earth 0개 → 안정감 부족". 차트 grounding의 실체 | 필수 |
| **Favorable Element** (용신) | 실천 조언 핵심 — "fire를 키워라 → 리더십·가시성". 유일한 actionable hint | 필수 |

**Post-MVP (너무 복잡, 설명 오버헤드 큼):**
- 십신(Ten Gods): 풍부하지만 영어 설명 비용이 큼 → 유료 심화 리딩에서
- 대운/소운(Luck Cycles): 프리미엄 "10년 운세" 기능으로
- 시주(Hour Pillar): 정확한 출생시간 없는 서양 유저 많음 → 선택 입력

---

## 2. System Prompt 구조

### 2-1. 차트 데이터 형식: JSON

```json
{
  "user_name": "Alex",
  "birth_date": "1995-06-15",
  "birth_time": "14:30",
  "birth_location": "Los Angeles, CA",
  "daymaster": {
    "element": "wood",
    "yin_yang": "yang",
    "heavenly_stem": "甲",
    "archetype": "Pioneer",
    "strength": "moderate"
  },
  "pillars": {
    "year":  { "stem": "wood",      "branch": "pig"    },
    "month": { "stem": "metal",     "branch": "horse"  },
    "day":   { "stem": "yang_wood", "branch": "rabbit" },
    "hour":  { "stem": "water",     "branch": "dragon" }
  },
  "elemental_balance": {
    "wood":  2,
    "fire":  1,
    "earth": 0,
    "metal": 2,
    "water": 2
  },
  "favorable_element": "fire",
  "current_luck_cycle": {
    "element": "fire",
    "branch":  "south",
    "period":  "2025–2035"
  }
}
```

**JSON 선택 이유:**
- LLM이 없는 필드를 "발명"할 수 없음 (환각 구조적 방지)
- 필드 추가·버전 관리 용이
- Prompt cache TTL 5분 — JSON은 변하지 않으므로 캐시 적중률 높음

### 2-2. 전체 System Prompt 스켈레톤

```
You are a warm, conversational K-Saju AI — an English-speaking guide to Korean
Four Pillars astrology (사주팔자). Your job: give the user grounded, specific,
encouraging readings based on THEIR chart data below.

<CHART_DATA>
[위 JSON]
</CHART_DATA>

## TONE GUARDRAILS
- Warm, supportive, encouraging. Never fear-mongering, never passive-aggressive.
- Every insight MUST trace back to a field in the JSON chart above.
- Explain WHY: "You have 0 earth → you may feel ungrounded because earth represents
  stability and routine."
- Self-explaining: define terms when they first appear. "Your Day Master is Yang Wood
  (甲木) — in Korean saju, this is your core elemental identity."
- If the chart doesn't support a claim, say so: "Your chart doesn't show strong [X]
  signals, so I'll stay honest and skip speculation."

## FORBIDDEN PATTERNS
- ❌ "You might..." without chart evidence
- ❌ "Ancient wisdom says..." (vague filler)
- ❌ Generic astrology copy not tied to this user's JSON
- ❌ Negative predictions without an actionable counterpoint

## RESPONSE PATTERN (Evidence → Interpretation → Action)
For every key insight:
1. State the evidence: "Your chart shows [field/value]."
2. Interpret it for real life: "This means [specific implication]."
3. Give one action: "So, this season/year, lean into [X]."
```

---

## 3. 리딩 유형별 프롬프트

### 3-1. 첫 리딩 — Day Master Archetype Card

**트리거:** 온보딩 직후 자동 생성. 공유용 카드의 텍스트 소스.

```
Generate a "Day Master Reading" for this user. Structure:

1. ARCHETYPE NAME (2–4 words, memorable, shareable)
   e.g., "Yang Wood Pioneer", "Yin Water Dreamer"

2. CORE IDENTITY (2–3 sentences)
   Ground in Day Master + strength + elemental balance.

3. YOUR GIFT (1 sentence) — the user's natural superpower from the chart.

4. YOUR EDGE (1 sentence) — the favorable element as a growth direction.
   Must reference the favorable_element field.

5. SHAREABLE ONE-LINER (for the card)
   Punchy, Gen Z tone. e.g., "I'm Yang Wood 甲木 — I grow through resistance."

Keep total under 120 words. Warm, specific, no generic platitudes.
```

### 3-2. 대화형 챗 — 후속 질문

**트리거:** 유저 자유 질문. 차트 JSON은 session 내내 캐시됨.

```
The user is asking a follow-up question. Their saju chart is already in CHART_DATA.

Answer their question by:
1. Identifying which chart field(s) are most relevant.
2. Explaining the connection to their question.
3. Giving a concrete, actionable answer.

If their question is about a person (friend, partner, boss), ask for that person's
Day Master if not provided — compatibility needs two charts.

Keep answers to 3–5 sentences. Conversational, not lecture-y.
```

### 3-3. 궁합 리딩 (Compatibility — 유료)

```
The user wants a compatibility reading between themselves and another person.

User's chart: [from CHART_DATA]
Partner's chart: [from PARTNER_CHART_DATA — same JSON schema]

Apply Five Element dynamics:
- Generating cycle (木→火→土→金→水→木): supportive relationship
- Controlling cycle (木→土→水→火→金→木): tension/challenge

Structure:
1. DYNAMIC TYPE: "Generating" or "Controlling" (be specific about which elements)
2. NATURAL STRENGTH: What the relationship naturally does well
3. NATURAL TENSION: Where the friction comes from (with empathy, not doom)
4. BRIDGE: One concrete action that uses their natural dynamic productively

Tone: hopeful, specific, never fatalistic. All relationships are workable.
```

---

## 4. 모델 라우팅 전략

| 리딩 유형 | 모델 | 이유 |
|---|---|---|
| Day Master 첫 리딩 | **claude-sonnet-4-6** | 공유 카드 = 브랜드 첫인상. 품질 최우선 |
| 데일리 운세 (배치) | **claude-haiku-4-5** | 매일 생성, 비용 최소화 |
| 후속 챗 질문 | **claude-haiku-4-5** | 속도·비용. 단순 해석은 Haiku로 충분 |
| 궁합 리딩 (유료) | **claude-sonnet-4-6** | 결제한 유저 → 품질 보장 |
| 풀 라이프 리포트 (유료) | **claude-sonnet-4-6** | 복잡한 대운 해석 필요 |

---

## 5. 비용 모델 (1,000 DAU 기준)

| 시나리오 | 일별 비용 | 월별 비용 |
|---|---|---|
| 캐싱 없음, Sonnet 전체 | ~$23/일 | ~$700/월 |
| 프롬프트 캐싱 + Haiku 후속 라우팅 | ~$8/일 | **~$240/월** |
| 위 + 데일리 배치(Batch API 50% 할인) | ~$5/일 | **~$150/월** |

**무료 티어 3질문/일 캡** = 비용 방어선이자 업셀 트리거.

**Break-even 계산 (보수적):**
- 1000 DAU, 3% 전환율 → 30 유료 유저 × $7/월 = $210 수익
- 최적화 후 LLM 비용 ~$150/월 → **초기부터 수익 흑자 가능**

---

## 6. 환각 방지 체크리스트

코드 구현 시 반드시:

- [ ] LLM output에 차트 JSON에 없는 숫자/날짜/이름이 있으면 response validation으로 catch
- [ ] 개인정보 필드(birth_date, location)를 output에 그대로 노출하지 않음
- [ ] `favorable_element`가 null일 때 fallback 텍스트 정의
- [ ] 시주(hour pillar) 입력 없으면 hour pillar 관련 주장 금지 (prompt에 명시)
- [ ] "medical/financial advice" 단정 문구 금지 (스토어 정책)

---

## 7. 연동 참고 (구현 시)

- 사주 계산 엔진: `yhj1024/manseryeok` (TypeScript) 또는 `alvamind/bazi-calculator`
- 결정론 엔진 → JSON serialize → system prompt에 주입
- Prompt caching: system prompt + CHART_DATA 블록에 `cache_control: {"type": "ephemeral"}` 마킹
- 모델 라우팅: 리딩 유형별 분기는 앱 레이어(Flutter → 백엔드 API)에서 처리
