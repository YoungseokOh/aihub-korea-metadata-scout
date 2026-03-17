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

- 처음 실행 시 Python 3.11 설치 확인
- `.venv`가 없거나 `pyproject.toml` 또는 `uv.lock`이 바뀐 경우에만 `uv sync --python 3.11 --extra dev`
- 이후에는 준비된 `.venv`의 `aihub-korea-scout`를 바로 실행

즉, 처음 사용하는 경우에도 `bash run.sh doctor`처럼 바로 시작할 수 있고, 두 번째 실행부터는 훨씬 빠르게 동작합니다.

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
| `FORCE_SYNC` | 선택 | `1`로 설정하면 `run.sh`가 캐시된 환경을 무시하고 다시 `uv sync`를 수행합니다. |

### 환경 변수 상세 설명

- `AIHUB_API_KEY`
  - 이 프로젝트의 Python 코드가 직접 외부 API를 호출하지는 않습니다.
  - 값이 설정되어 있으면 `aihubshell` 실행 시 자식 프로세스 환경 변수 `AIHUB_APIKEY`로 전달합니다.
  - 메타데이터-only 흐름에서는 없어도 동작하는 경우가 많지만, 로컬 `aihubshell` 환경이나 계정 상태에 따라 필요할 수 있습니다.
- `AIHUB_SHELL_PATH`
  - 공식 `aihubshell` 실행 파일의 위치를 강제로 지정합니다.
  - 예를 들어 시스템 PATH에 여러 버전이 있거나, 사용자 로컬 경로에 별도로 설치한 경우 이 값을 명시하면 그 경로를 우선 사용합니다.
  - `bootstrap`도 같은 값을 설치 대상 경로로 사용합니다.
- `AIHUB_OUTPUT_DIR`
  - 전체 산출물의 루트 폴더입니다.
  - 기본값은 저장소 루트 기준 `./data`입니다.
  - 원본 캐시, 정규화 JSON, 생성 Markdown이 모두 이 경로 아래에 정리됩니다.
  - 라이브 테스트를 저장소 밖에서 돌리고 싶다면 예를 들어 `AIHUB_OUTPUT_DIR=/tmp/aihub-smoke/data`처럼 지정하면 됩니다.
- `AIHUB_CACHE_DIR`
  - 원본 `aihubshell` stdout 캐시를 따로 분리하고 싶을 때 사용합니다.
  - 기본값은 `AIHUB_OUTPUT_DIR/raw`입니다.
  - 따로 지정하지 않으면 raw 캐시가 출력 루트 안에 함께 저장됩니다.
- `PYTHON_VERSION`
  - `run.sh`가 준비할 Python major/minor 버전입니다.
  - 기본값은 `3.11`이며, 첫 실행 시 `.venv`가 없거나 버전이 다르면 이 값을 기준으로 환경을 맞춥니다.
  - 보통은 바꿀 필요가 없고, 팀에서 3.12로 올린 경우처럼 런타임 정책이 바뀔 때만 조정하면 됩니다.
- `FORCE_SYNC`
  - `1`로 설정하면 `run.sh`가 기존 `.venv`를 재사용하지 않고 다시 `uv sync`를 수행합니다.
  - 의존성을 새로 맞추고 싶거나 `.venv` 상태가 의심될 때만 사용하면 됩니다.

예시:

```bash
AIHUB_OUTPUT_DIR=/tmp/aihub-smoke/data ./run.sh doctor
AIHUB_SHELL_PATH=$HOME/.local/bin/aihubshell ./run.sh list --limit 5
FORCE_SYNC=1 ./run.sh doctor
```

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
bash run.sh scan --all
bash run.sh build-index
```

## 전체 데이터셋을 전부 탐색하려면

가장 간단한 방법은 아래 순서입니다.

```bash
./run.sh bootstrap
./run.sh doctor
./run.sh scan --all
```

동작 방식은 다음과 같습니다.

1. `list` 단계로 전체 데이터셋 목록을 가져옵니다.
2. 각 `dataset_key`에 대해 `inspect`와 같은 메타데이터 조회를 반복합니다.
3. 데이터셋별 JSON과 Markdown 브리프를 저장합니다.
4. 마지막에 전체 요약 카탈로그를 다시 빌드합니다.

주의할 점:

- `scan` 기본값은 `--limit 20`이므로 옵션 없이 실행하면 처음 20개만 처리합니다.
- `--all`을 주면 목록에 나온 전체 데이터셋을 끝까지 순회합니다.
- 이미 생성된 `normalized/datasets/<datasetkey>.json`이 있으면 기본적으로 재조회하지 않고 재사용합니다.
- 모든 데이터를 다시 조회하고 싶으면 `./run.sh scan --all --refresh`를 사용하면 됩니다.

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

### 각 폴더에 무엇이 쌓이는가

- `raw/list/latest.txt`
  - 가장 최근 전체 목록 조회의 원본 stdout입니다.
- `raw/list/latest.meta.json`
  - 위 원본 stdout을 생성한 명령, 시각, 해시, stderr 같은 추적 정보입니다.
- `raw/datasets/<datasetkey>.txt`
  - 특정 데이터셋 상세 조회의 원본 stdout입니다.
- `raw/datasets/<datasetkey>.meta.json`
  - 해당 상세 조회 명령의 추적 정보입니다.
- `normalized/list/latest.json`
  - 목록 파싱 결과입니다. `dataset_key`, 제목, 카테고리/모달리티 추정, 파싱 경고가 들어 있습니다.
- `normalized/datasets/<datasetkey>.json`
  - 개별 데이터셋의 핵심 결과물입니다. 파일 수, 크기, 샘플 경로, notices, metadata lines, score, business analysis, raw cache 경로가 들어 있습니다.
- `normalized/scans/<timestamp>.json`
  - 한 번의 `scan` 실행에 대한 manifest입니다. 언제 돌렸는지, 몇 개를 선택했고 몇 개를 처리/건너뜀/실패했는지 기록합니다.
- `normalized/catalog.json`
  - 전체 수집 결과를 바탕으로 만든 랭킹 카탈로그의 JSON 버전입니다.
- `generated/datasets/<datasetkey>-<slug>.md`
  - 사람이 읽기 쉬운 데이터셋 브리프입니다. 메타데이터 기반 요약, 사용 가능성, 사업성 탐색, 점수가 들어 있습니다.
- `generated/index/dataset-catalog.md`
  - 전체 데이터셋을 점수와 특성별로 묶은 읽기용 카탈로그입니다.

즉, 정리 방식은 `원본 캐시 -> 정규화 JSON -> 사람이 읽는 Markdown`의 3단계입니다.

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
