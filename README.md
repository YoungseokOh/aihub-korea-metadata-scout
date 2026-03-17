# aihub-korea-metadata-scout

`aihub-korea-metadata-scout`는 AI-Hub Korea 데이터셋을 메타데이터만으로 탐색하는 로컬 중심 도구입니다.
공식 `aihubshell`을 사용해서 다음 작업을 수행합니다.

- 데이터셋 목록 조회
- 데이터셋별 파일 트리/메타데이터 확인
- 구조화된 JSON 정규화
- 데이터셋 요약 Markdown 생성
- 메타데이터 기반의 가벼운 사업성 탐색과 랭킹

이 프로젝트는 의도적으로 보수적으로 설계되어 있습니다. 실제 데이터 다운로드는 하지 않고, 다운로드 명령도 제공하지 않으며, 제목/메타데이터 라인/파일 트리 밖의 의미를 추측하지 않습니다.

## 이 프로젝트가 하는 일

- 공식 `aihubshell` 설치 또는 검증
- 안전한 메타데이터 명령만 실행
  - `-help`
  - `-mode l`
  - `-mode l -datasetkey <id>`
- 원본 stdout 캐시 저장
- 방어적인 파싱을 통해 구조화된 JSON 생성
- 데이터셋별 Markdown 브리프 생성
- 수집된 결과를 기준으로 카탈로그 Markdown/JSON 생성

## 이 프로젝트가 하지 않는 일

- 데이터셋 다운로드
- `aihubshell -mode d` 또는 패키지 다운로드 모드 호출
- 다운로드용 placeholder 코드 추가
- 비공식 API 역공학
- 실제 데이터 내용을 보지 않고 품질/라벨 의미를 단정

## 왜 메타데이터 전용인가

AI-Hub 데이터셋은 크기가 크거나 승인/스토리지/전처리 비용이 클 수 있습니다. 초기 탐색 단계에서는 실제 다운로드 이전에 아래 질문에 빠르게 답하는 것이 더 중요할 때가 많습니다.

- 어떤 데이터셋이 존재하는가
- 겉보기 크기는 어느 정도인가
- 파일 구조는 단순한가 복잡한가
- 라벨/원천, 학습/검증 분리가 보이는가
- 사업적으로 흥미로운 후보는 무엇인가

이 저장소는 그 목적에 맞게 메타데이터만 사용합니다.

## 사전 요구사항

- Linux 또는 macOS 셸 환경
- `uv`
- `curl`
- Python 3.11+

CLI는 런타임에서도 Python 버전을 검사하며, 3.11 미만이면 설치 가이드를 출력하고 종료합니다.

Python 3.11이 없다면 먼저 실행하세요.

```bash
uv python install 3.11
```

## 가장 간단한 실행 방법

루트의 `run.sh`를 사용하면 됩니다. 실행 환경에 따라 `./run.sh` 대신 `bash run.sh` 형태가 더 안전할 수 있습니다.

```bash
bash run.sh --help
bash run.sh bootstrap
bash run.sh doctor
bash run.sh list --limit 5
bash run.sh inspect --datasetkey 593
bash run.sh summarize --datasetkey 593
bash run.sh scan --limit 20
bash run.sh build-index
```

`run.sh`는 내부적으로 다음을 처리합니다.

- Python 3.11 설치 확인
- `uv sync --python 3.11 --extra dev`
- `uv run aihub-korea-scout ...` 실행

즉, 처음 사용하는 경우에도 `bash run.sh doctor`처럼 바로 시작할 수 있습니다.

## 빠른 시작

```bash
git clone https://github.com/YoungseokOh/aihub-korea-metadata-scout.git
cd aihub-korea-metadata-scout
bash run.sh bootstrap
bash run.sh doctor
```

`bootstrap`는 다음을 수행합니다.

1. Python 3.11 환경 준비
2. 프로젝트 의존성 동기화
3. 공식 `aihubshell` 다운로드
4. 실행 권한 부여
5. 메타데이터 목록 명령으로 설치 검증

기본 설치 경로는 `~/.local/bin/aihubshell`이며, `AIHUB_SHELL_PATH`가 설정되어 있으면 그 경로를 사용합니다.

## Make 명령 사용 방법

원하면 기존 `make` 명령도 그대로 사용할 수 있습니다.

```bash
make bootstrap
make doctor
make test
make scan
```

## 환경 변수

`.env.example`을 복사해 `.env`로 사용할 수 있습니다.

```bash
cp .env.example .env
```

| 변수명 | 필수 여부 | 설명 |
| --- | --- | --- |
| `AIHUB_API_KEY` | 선택 | `aihubshell`에 `AIHUB_APIKEY`로 전달됩니다. 메타데이터 조회만 할 때는 보통 없어도 됩니다. |
| `AIHUB_SHELL_PATH` | 선택 | `aihubshell` 실행 파일 경로를 직접 지정합니다. bootstrap 설치 경로로도 사용됩니다. |
| `AIHUB_OUTPUT_DIR` | 선택 | 출력 루트 디렉터리입니다. 기본값은 `./data`입니다. |
| `AIHUB_CACHE_DIR` | 선택 | 원본 stdout 캐시 디렉터리입니다. 기본값은 `./data/raw`입니다. |
| `PYTHON_VERSION` | 선택 | `run.sh`가 사용할 Python 버전입니다. 기본값은 `3.11`입니다. |

## 명령 예시

### 설치/진단

```bash
bash run.sh bootstrap
bash run.sh doctor
```

### 목록 조회

```bash
bash run.sh list
bash run.sh list --limit 10
```

### 개별 데이터셋 분석

```bash
bash run.sh inspect --datasetkey 593
bash run.sh summarize --datasetkey 593
```

### 전체 스캔 및 카탈로그 생성

```bash
bash run.sh scan --limit 20
bash run.sh build-index
```

## 출력 구조

```text
data/
├─ raw/
│  ├─ list/latest.txt
│  ├─ list/latest.meta.json
│  ├─ datasets/<datasetkey>.txt
│  └─ datasets/<datasetkey>.meta.json
├─ normalized/
│  ├─ list/latest.json
│  ├─ datasets/<datasetkey>.json
│  ├─ scans/<timestamp>.json
│  └─ catalog.json
└─ generated/
   ├─ datasets/<datasetkey>-<slug>.md
   └─ index/dataset-catalog.md
```

## 파서 동작 원칙

- `aihubshell` 출력에는 배너, 공지, 한국어/영어 혼합 텍스트, 박스 드로잉 문자가 포함될 수 있습니다.
- 파서는 실패보다 부분 성공을 우선합니다.
- 정확히 해석하지 못한 라인은 `parse_warnings`에 남깁니다.
- 존재하지 않는 데이터셋 페이지는 `parse_status=error`로 저장합니다.
- 파일 크기 합계는 출력에 실제로 보인 크기만 합산합니다.

## 점수와 사업성 분석 주의사항

- 점수는 탐색용 heuristic입니다.
- 기회 점수, 난이도 점수, 데이터 준비도 점수는 정밀 평가가 아닙니다.
- 제목, 파일명, 구조, 용량, 라벨/원천 분리, 학습/검증 분리 같은 가시 정보만 사용합니다.
- 생성 문구는 항상 메타데이터 기반 추정이라는 전제를 유지합니다.
- 라이선스, 승인 범위, 정책 적합성은 별도 검토가 필요합니다.

## 개발 명령

```bash
uv run ruff check .
uv run pytest
```

## 샘플 산출물

테스트 fixture 기반의 결정론적 샘플 산출물이 저장소에 포함되어 있습니다.

- `data/normalized/datasets/86.json`
- `data/normalized/datasets/88.json`
- `data/generated/datasets/86-감성대화.md`
- `data/generated/datasets/88-공공행정문서-ocr.md`
- `data/generated/index/dataset-catalog.md`

이 파일들은 라이브 스캔 결과가 아니라 고정 fixture 기반으로 생성된 예시입니다.

## 구조 요약

- `shell/`: 공식 `aihubshell` 설치, 실행, 파싱
- `pipeline/`: list, inspect, summarize, catalog build
- `storage/`: raw cache, JSON, Markdown 저장
- `scoring/`: heuristic 기반 분석
- `cli.py`: Typer CLI 진입점

아키텍처는 단순성을 우선합니다. 외부 셸 경계 하나, 파서 경계 하나, 정규화된 출력 포맷 하나, 보고서 계층 하나로 유지합니다.

## 추가 문서

상세 문서는 [`docs/`](./docs/README.md) 아래에 있습니다.
