# 드론 자율항법을 위한 영상 및 센서 데이터(SLAM DATA)

## Basic Info
- Dataset Key: `647`
- Source Command: `/root/.local/bin/aihubshell -mode l -datasetkey 647`
- Collected At: `2026-03-17T08:40:55.918918+00:00`
- Parse Status: `success`
- Inferred tags:
  - `computer-vision`
  - `video`
  - `영상`
  - `slam`
  - `드론`
  - `센서`
  - `위한`
  - `자율항법을`
  - `a2`
  - `a3`
  - `a4`
  - `tl1`
  - `tl2`
  - `tl3`
  - `ts1`
  - `ts2`

## File Overview
- File count: `12`
- Total known size: `174.8 GB`
- Representative file paths:
  - `092.드론 자율항법을 위한 영상 및 센서 데이터(SLAM DATA)/01.데이터/1.Training/라벨링데이터/TL1_A2(주택저밀집지역).zip`
  - `092.드론 자율항법을 위한 영상 및 센서 데이터(SLAM DATA)/01.데이터/1.Training/라벨링데이터/TL2_A3(산간,도서지역).zip`
  - `092.드론 자율항법을 위한 영상 및 센서 데이터(SLAM DATA)/01.데이터/1.Training/라벨링데이터/TL3_A4(농촌,기타지역).zip`
  - `092.드론 자율항법을 위한 영상 및 센서 데이터(SLAM DATA)/01.데이터/1.Training/원천데이터/TS1_A2(주택저밀집지역).zip`
  - `092.드론 자율항법을 위한 영상 및 센서 데이터(SLAM DATA)/01.데이터/1.Training/원천데이터/TS2_A3(산간,도서지역).zip`
- Notices / warnings:
  - 공지사항은 보이지 않았습니다.

## What This Dataset Appears To Be
제목과 파일 트리를 기준으로 보면 이 데이터셋은 `computer-vision` 성격의 `video` 자료로 보입니다. 확인 가능한 파일은 12개이며 알려진 총 용량은 174.8 GB입니다. training/validation 분리가 보여서 기본 실험 파이프라인을 구성하기는 쉬워 보입니다. 세부 의미 해석은 하지 않았고, 이 설명은 제목과 파일 트리만으로 추론했습니다 (inferred from title and file tree only).

## Potential Use Cases
- 내부 데이터 파이프라인 실험
- 도메인 특화 검색/분류 모델 평가
- 수직형 AI 제품의 초기 검증셋

## Business Model Exploration
- likely customer types:
  - 수직형 AI 제품팀
  - 데이터 중심 스타트업
  - 내부 분석 플랫폼 팀
- possible product ideas:
  - 내부 데이터 파이프라인 실험
  - 도메인 특화 검색/분류 모델 평가
  - 수직형 AI 제품의 초기 검증셋
- monetization paths:
  - 월 구독
  - 사용량 과금 API
  - 전문 서비스 결합 판매
- why it could be interesting commercially:
  - 좁은 문제를 빠르게 실험하는 데는 의미가 있을 수 있습니다.
  - 구조가 드러난 파일 트리는 초기 타당성 검토 속도를 높여 줍니다.
- why it might fail commercially:
  - 실제 내용 품질이 기대보다 낮으면 사업화 가정이 쉽게 무너질 수 있습니다.
  - 메타데이터 기반 해석이라 현업 니즈와 어긋날 가능성을 열어 둬야 합니다.

## Practicality Assessment
- training/validation 분리가 보여서 기본 실험 파이프라인을 구성하기는 쉬워 보입니다.
- 라벨링 데이터와 원천 데이터가 모두 보여서 지도학습 준비도가 상대적으로 높아 보입니다.
- 표시된 총 용량이 매우 커서 저장소와 처리 비용이 빠르게 증가할 가능성이 큽니다.
- 실사용 전까지 저장소/배치 처리 설계를 먼저 잡는 편이 안전해 보입니다.
- 법률·정책 적합성은 별도 확인이 필요합니다.
- legal/policy caution placeholder: License and policy suitability must be validated separately.

## Scores
- Opportunity score: `3` / 10
- Build difficulty: `8` / 10
- Data readiness: `6` / 10
- Score reasons:
  - 영상/3D 계열은 저장·전처리·서빙 부담이 큰 편입니다.
  - 표시된 용량이 매우 커서 초기 실험 비용이 큽니다.
  - 라벨링 데이터가 보여 활용 가설을 세우기 쉽습니다.

## Raw Metadata Snapshot
```json
{
  "dataset_key": 647,
  "title": "드론 자율항법을 위한 영상 및 센서 데이터(SLAM DATA)",
  "tags": [
    "computer-vision",
    "video",
    "영상",
    "slam",
    "드론",
    "센서",
    "위한",
    "자율항법을",
    "a2",
    "a3"
  ],
  "category_guess": "computer-vision",
  "modality_guess": "video",
  "file_count": 12,
  "total_size_bytes": 187743338496,
  "human_size": "174.8 GB",
  "sample_file_paths": [
    "092.드론 자율항법을 위한 영상 및 센서 데이터(SLAM DATA)/01.데이터/1.Training/라벨링데이터/TL1_A2(주택저밀집지역).zip",
    "092.드론 자율항법을 위한 영상 및 센서 데이터(SLAM DATA)/01.데이터/1.Training/라벨링데이터/TL2_A3(산간,도서지역).zip",
    "092.드론 자율항법을 위한 영상 및 센서 데이터(SLAM DATA)/01.데이터/1.Training/라벨링데이터/TL3_A4(농촌,기타지역).zip",
    "092.드론 자율항법을 위한 영상 및 센서 데이터(SLAM DATA)/01.데이터/1.Training/원천데이터/TS1_A2(주택저밀집지역).zip",
    "092.드론 자율항법을 위한 영상 및 센서 데이터(SLAM DATA)/01.데이터/1.Training/원천데이터/TS2_A3(산간,도서지역).zip"
  ],
  "parse_status": "success",
  "parse_warnings": [],
  "notices": []
}
```