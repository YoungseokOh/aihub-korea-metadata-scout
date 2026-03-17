# 공공행정문서 OCR

## Basic Info
- Dataset Key: `88`
- Source Command: `aihubshell -mode l -datasetkey 88`
- Collected At: `2026-03-17T03:00:00+00:00`
- Parse Status: `success`

## File Overview
- File count: `23`
- Total known size: `386.0 GB`
- Representative file paths:
  - `032.공공행정문서 OCR/01.데이터/01.Training/[라벨]train.zip`
  - `032.공공행정문서 OCR/01.데이터/01.Training/[라벨]train_partly_labling.zip`
  - `032.공공행정문서 OCR/01.데이터/01.Training/[원천]train_partly_labeling_01.zip`
  - `032.공공행정문서 OCR/01.데이터/01.Training/[원천]train_partly_labeling_02.zip`
  - `032.공공행정문서 OCR/01.데이터/01.Training/[원천]train_partly_labeling_03.zip`
- Notices / warnings:
  - 공지사항은 보이지 않았습니다.

## What This Dataset Appears To Be
제목과 파일 트리를 기준으로 보면 이 데이터셋은 `ocr/document` 성격의 `text` 자료로 보입니다. 확인 가능한 파일은 23개이며 알려진 총 용량은 386.0 GB입니다. training/validation 분리가 보여서 기본 실험 파이프라인을 구성하기는 쉬워 보입니다. 세부 의미 해석은 하지 않았고, 이 설명은 제목과 파일 트리만으로 추론했습니다 (inferred from title and file tree only).

## Potential Use Cases
- 문서 인입 자동화 및 검색 보조
- 공공기관 기록물 분류/검수 워크플로우
- 규정 문서 추출형 B2B SaaS

## Business Model Exploration
- likely customer types:
  - 공공기관
  - 문서 자동화 SaaS 팀
  - 엔터프라이즈 백오피스 운영팀
- possible product ideas:
  - 문서 인입 자동화 및 검색 보조
  - 공공기관 기록물 분류/검수 워크플로우
  - 규정 문서 추출형 B2B SaaS
- monetization paths:
  - 엔터프라이즈 구독
  - 프로젝트 구축/커스터마이징
  - 검수 워크플로우 사용량 과금
- why it could be interesting commercially:
  - 좁은 문제를 빠르게 실험하는 데는 의미가 있을 수 있습니다.
  - 구조가 드러난 파일 트리는 초기 타당성 검토 속도를 높여 줍니다.
- why it might fail commercially:
  - 실제 내용 품질이 기대보다 낮으면 사업화 가정이 쉽게 무너질 수 있습니다.
  - 메타데이터 기반 해석이라 현업 니즈와 어긋날 가능성을 열어 둬야 합니다.

## Practicality Assessment
- training/validation 분리가 보여서 기본 실험 파이프라인을 구성하기는 쉬워 보입니다.
- 라벨링 데이터와 원천 데이터가 모두 보여서 지도학습 준비도가 상대적으로 높아 보입니다.
- 압축 파일 조각이 많아 보여 파일 정리와 전처리 부담이 커질 수 있습니다.
- 표시된 총 용량이 매우 커서 저장소와 처리 비용이 빠르게 증가할 가능성이 큽니다.
- 실사용 전까지 저장소/배치 처리 설계를 먼저 잡는 편이 안전해 보입니다.
- 법률·정책 적합성은 별도 확인이 필요합니다.
- legal/policy caution placeholder: License and policy suitability must be validated separately.

## Scores
- Opportunity score: `6` / 10
- Build difficulty: `8` / 10
- Data readiness: `5` / 10
- Score reasons:
  - 상업적 수요가 반복적으로 발생하는 문제 영역으로 보입니다.
  - 표시된 용량이 매우 커서 초기 실험 비용이 큽니다.
  - 압축 조각이 많아 전처리 파이프라인이 필요해 보입니다.
  - 라벨링 데이터가 보여 활용 가설을 세우기 쉽습니다.

## Raw Metadata Snapshot
```json
{
  "dataset_key": 88,
  "title": "공공행정문서 OCR",
  "category_guess": "ocr/document",
  "modality_guess": "text",
  "file_count": 23,
  "total_size_bytes": 414452809728,
  "human_size": "386.0 GB",
  "sample_file_paths": [
    "032.공공행정문서 OCR/01.데이터/01.Training/[라벨]train.zip",
    "032.공공행정문서 OCR/01.데이터/01.Training/[라벨]train_partly_labling.zip",
    "032.공공행정문서 OCR/01.데이터/01.Training/[원천]train_partly_labeling_01.zip",
    "032.공공행정문서 OCR/01.데이터/01.Training/[원천]train_partly_labeling_02.zip",
    "032.공공행정문서 OCR/01.데이터/01.Training/[원천]train_partly_labeling_03.zip"
  ],
  "parse_status": "success",
  "parse_warnings": [],
  "notices": []
}
```
