---
name: aihub-app-ideation
description: >-
  Generate detailed, solo-developer-focused app/web product ideas from AI-Hub
  Korea dataset metadata. Use when the user wants to brainstorm app ideas from a
  dataset, asks "이 데이터셋으로 뭘 만들 수 있어 / 앱 아이디어 뽑아줘", "what can I build
  with dataset X", or wants to judge feasibility and rank ideas. Always produces
  at least 5 ideas per dataset with a rich per-idea spec, metadata-only.
---

# AI-Hub App Ideation Skill

## Purpose

Turn AI-Hub Korea dataset **metadata** into concrete, buildable **app/web product
ideas** — at least 5 per dataset — each with a detailed spec and an honest
feasibility judgement. This skill is the deep, structured version of the
`ideate` CLI command in this repo.

Use it when the user wants to explore "what could I build with this dataset?"

## Hard Requirements

1. **Minimum 5 ideas per dataset.** Never return fewer. If the metadata is thin,
   still produce 5 and mark the weak ones `no-go` with the reason.
2. **Metadata only.** Reason strictly from title, inferred tags, file tree, file
   sizes, train/val split, label/source presence. Never claim dataset contents,
   label schemas, licenses, or quality you cannot see. State that every judgement
   is a metadata-only estimate.
3. **Each idea uses the full per-idea template below.** "More detailed than a
   one-liner" is the bar — no bare titles.
4. **Honest feasibility.** Score and verdict must reflect reality, including the
   solo-developer lens below. Do not inflate.
5. **Always scan competitor apps.** Every idea must include a real competitor
   check — never assume a niche is empty. Search the App Store / Google Play and
   the web for existing apps (Korean AND global/English), name 2–4 concrete ones
   with what they do and where they fall short, and let that gap drive the
   `차별화 무기`. "No competitor found" is a valid result only after an actual
   search, and is itself a warning (small/non-existent market), not a green light.

## Default Lens: Solo Developer Building Apps

Unless the user says otherwise, assume the builder is **one person shipping B2C
apps** (mobile/web, self-serve distribution). Score ideas through this lens:

- **Favor**: image classification / text tasks that run cheaply or on-device;
  clear consumer hook; simple monetization (subscription / IAP); Korea-specific
  data as a moat against global apps.
- **Down-rank (usually unrealistic for a solo app builder)**: anything needing
  B2B/B2G sales, on-prem hardware/sensor/factory/field access, or heavy
  regulation/liability (medical diagnosis, face recognition, financial advice).
  Examples to treat as low-priority for this persona: 전력설비, 공공기관 납품,
  특허/지식재산 전문툴, 제조 불량검출 라인, 위성/교통 인프라.
- If an idea is attractive but unrealistic for a solo builder, say so explicitly
  rather than silently ranking it high.

When the user states a different persona (enterprise, team, research), adapt the
lens accordingly and say which lens you used.

## Workflow

### 1. Acquire dataset metadata
Prefer the repo's own pipeline so reasoning is grounded in real parsed metadata:

```bash
./run.sh inspect --datasetkey <KEY>     # parses + normalizes, writes summary JSON
```

Or reuse an existing summary at `data/normalized/datasets/<KEY>.json`. If neither
is available (no aihubshell), work from whatever metadata the user provides, and
note that keys/sizes are unverified.

Read from the summary: `title`, `category_guess`, `modality_guess`, `tags`,
`file_count`, `human_size`, `sample_file_paths`, `metadata_lines`,
`parse_status`, train/val and label/source presence.

### 2. Classify the dataset
State in one or two lines: domain, modality (or "unknown — verify by opening one
source zip"), rough size class, and supervised-readiness (labels + train/val).
Flag uncertainty honestly (e.g. "통합 데이터" → modality could be images or sensors).

### 3. Generate at least 5 ideas
Spread ideas across **different angles** — don't give five variants of one app.
Cover a mix of: consumer utility, creator/content, education/learning,
wellness/care, and a "data-as-moat" or niche angle. Each idea uses the template.

### 4. Competitor / market scan (required)
For each idea, do a real search before scoring — do not reason from memory alone:

- Search app stores and the web for existing apps, both **Korean** (점신, 포스텔러,
  네이버/카카오 등) and **global/English**. Useful queries: "<concept> app",
  "<concept> 앱", "<concept> App Store / Google Play".
- If the user has a market-scouting repo (e.g. `finding-cash-cow-android` —
  Play Store scraping/analysis), reuse its data when it's in session scope.
- Record 2–4 concrete competitors per idea: name, platform, what they do, price/
  monetization if visible, and the **gap** they leave. Note incumbents that make
  a head-on solo entry unrealistic (e.g. a category leader with huge revenue).
- Turn the gap into the idea's `차별화 무기`, and let competitive density feed the
  `opportunity_score` (crowded + strong incumbents → lower; real unmet gap → higher).
- An honestly empty niche is a yellow flag (likely small market), not a win.

### 5. Score and judge each idea
Give three 1–10 scores and a verdict:
- `opportunity_score` — market pull / consumer demand
- `feasibility_score` — how realistically a solo dev ships it (infra, cost, skill)
- `data_fit_score` — how well the dataset actually supports the idea
- `feasibility`: `go` | `maybe` | `no-go`

### 6. Rank and recommend
Rank the ideas (a simple combined weighting: opportunity 0.45, feasibility 0.35,
data-fit 0.20 — same as the repo's `combined_score`). Recommend the top 1–2 for a
solo builder and say why, plus the single biggest risk for each.

## Per-Idea Template (use all fields)

```
### <n>. <앱 이름> — <go|maybe|no-go>
- 한 줄 소개: <one-line pitch>
- 형태: app | web | both
- 타겟 사용자: <who, specifically>
- 핵심 기능: <3–5 features>
- 데이터 활용: 이 데이터셋의 무엇(라벨/모달리티/구조)을 어떤 모델 태스크로 쓰는지
- 모델 · 추론 비용: 온디바이스 가능 여부 / 학습 필요 여부 / 솔로 예산에서 현실적인지
- 솔로 실현성: 혼자 출시 가능한 이유 또는 막히는 지점
- MVP 흐름: 화면/단계 3–5개
- 수익 모델: 구독 / IAP / 광고 / 제휴
- 경쟁 앱: 실제 검색으로 찾은 기존 앱 2–4개 (국내+글로벌) — 이름·플랫폼·하는 일·빈틈. 없으면 "검색했으나 없음(=시장 작을 위험)"
- 차별화 무기: 위 경쟁 앱이 못 채운 빈틈을 어떻게 공략하는가 (특히 한국 특화 우위)
- 리스크: 2–3개 + 회피책
- 점수: 기회 N/10 · 실현 N/10 · 데이터적합 N/10
```

## Multiple datasets

When given several datasets, ideate each (≥5 ideas each), then build a
cross-dataset ranking: which dataset offers the strongest solo-app opportunity,
using each dataset's best idea. The repo command for the aggregate view:

```bash
./run.sh ideate-rank
```

## Using the automated pipeline

The repo can generate and persist this automatically (LM Studio / OpenAI /
Anthropic providers):

```bash
./run.sh ideate --datasetkey <KEY> --ideas 5            # local LM Studio (default)
./run.sh ideate --datasetkey <KEY> --provider anthropic # Claude
./run.sh ideate-rank                                    # rank datasets
```

Artifacts: `data/normalized/ideation/<KEY>.json` and
`data/generated/ideation/<KEY>-<slug>.md`. When you run ideation manually (no
LLM key), follow the same schema and template so output stays consistent with the
pipeline. The pipeline prompt also enforces the ≥5-idea and solo-lens rules.

## Cautions

- License, approval scope, and policy fit are out of scope for metadata — always
  flag them as "verify separately".
- Mental-health / medical / safety ideas: position as journaling/logging/wellness,
  never diagnosis; add a crisis-resource / disclaimer note.
- Keep scores honest; a list where everything is `go` is a failed analysis.

## Before Finishing

- Confirm every dataset got **≥5 ideas**, each with the full template.
- Confirm each idea has a **competitor scan from a real search** (≥2 named apps or
  an explicit "searched, none found" note).
- Confirm the solo-app lens was applied (or the chosen lens was stated).
- End with a ranked recommendation and the top risk per recommended idea.
