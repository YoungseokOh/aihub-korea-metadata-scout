from __future__ import annotations

from collections.abc import Iterable

from aihub_korea_metadata_scout.models import DatasetEntry, DatasetSummary

MODALITY_RULES = [
    ("multimodal", ("멀티모달", "vqa", "질의응답", "vision-language")),
    ("3d/lidar", ("라이다", "lidar", "3d", "lightfield", "ar/vr")),
    ("video", ("영상", "비디오", "video", "동영상", "방송")),
    ("audio", ("음성", "speech", "발화", "수어")),
    ("text", ("텍스트", "말뭉치", "지식", "문제", "요약", "문서")),
    ("image", ("이미지", "ocr", "x-ray", "안면", "피부", "사진")),
]

CATEGORY_RULES = [
    ("ocr/document", ("ocr", "문서", "공공행정", "글자체")),
    ("speech/dialogue", ("음성", "대화", "콜센터", "상담", "발화", "수어")),
    ("education", ("교육", "교과", "문제", "풀이")),
    ("legal/compliance", ("법률", "민원", "의학지식", "지식베이스")),
    ("medical", ("x-ray", "의학", "피부질환", "종양", "필수의료")),
    ("agriculture/aquaculture", ("양식장", "농산어촌", "식품소재", "농장", "반려견")),
    ("robotics", ("로봇", "인터랙션")),
    ("industrial/operations", ("물류", "시뮬레이션", "스마트", "작전", "리튬", "경계")),
    ("computer-vision", ("이미지", "영상", "객체", "랜드마크", "안면")),
    ("nlp/knowledge", ("텍스트", "요약", "질의응답", "말뭉치", "지식")),
]


def _normalize_texts(*parts: Iterable[str] | str | None) -> str:
    items: list[str] = []
    for part in parts:
        if part is None:
            continue
        if isinstance(part, str):
            items.append(part.casefold())
            continue
        items.extend(item.casefold() for item in part if item)
    return " ".join(items)


def infer_modality(
    title: str, file_paths: Iterable[str], metadata_lines: Iterable[str]
) -> str | None:
    haystack = _normalize_texts(title, file_paths, metadata_lines)
    for label, keywords in MODALITY_RULES:
        if any(keyword.casefold() in haystack for keyword in keywords):
            return label
    return None


def infer_category(
    title: str, file_paths: Iterable[str], metadata_lines: Iterable[str]
) -> str | None:
    haystack = _normalize_texts(title, file_paths, metadata_lines)
    for label, keywords in CATEGORY_RULES:
        if any(keyword.casefold() in haystack for keyword in keywords):
            return label
    return None


def enrich_entry(entry: DatasetEntry) -> DatasetEntry:
    entry.modality_guess = infer_modality(entry.title, (), ())
    entry.category_guess = infer_category(entry.title, (), ())
    return entry


def summarize_structure(summary: DatasetSummary) -> list[str]:
    structure_notes: list[str] = []
    all_paths = [item.path for item in summary.files]
    lower_paths = [path.casefold() for path in all_paths]

    if any("training" in path for path in lower_paths) and any(
        "validation" in path for path in lower_paths
    ):
        structure_notes.append(
            "training/validation 분리가 보여서 기본 실험 파이프라인을 구성하기는 쉬워 보입니다."
        )
    if any("라벨" in path or "label" in path for path in all_paths) and any(
        "원천" in path or "source" in path.casefold() for path in all_paths
    ):
        structure_notes.append(
            "라벨링 데이터와 원천 데이터가 모두 보여서 지도학습 준비도가 상대적으로 높아 보입니다."
        )
    if summary.file_count >= 20:
        structure_notes.append(
            "압축 파일 조각이 많아 보여 파일 정리와 전처리 부담이 커질 수 있습니다."
        )
    if summary.total_size_bytes and summary.total_size_bytes >= 100 * 1024**3:
        structure_notes.append(
            "표시된 총 용량이 매우 커서 저장소와 처리 비용이 빠르게 증가할 가능성이 큽니다."
        )
    if not structure_notes:
        structure_notes.append(
            "파일 트리 정보가 제한적이어서 구조 판단은 보수적으로 해석해야 합니다."
        )
    return structure_notes


def build_inferred_summary(summary: DatasetSummary) -> str:
    modality = summary.modality_guess or "명확하지 않은 형태"
    category = summary.category_guess or "범용 데이터"
    structure_hint = summarize_structure(summary)[0]
    if summary.file_count == 0:
        return (
            f"파일 목록이 충분히 보이지 않아 상세 해석은 어렵습니다. "
            f"제목 기준으로는 `{category}` 성격의 `{modality}` 데이터로 추정됩니다. "
            "이 설명은 제목과 파일 트리만으로 추론했습니다 "
            "(inferred from title and file tree only)."
        )
    return (
        f"제목과 파일 트리를 기준으로 보면 이 데이터셋은 "
        f"`{category}` 성격의 `{modality}` 자료로 보입니다. "
        f"확인 가능한 파일은 {summary.file_count}개이며 "
        f"알려진 총 용량은 {summary.human_size}입니다. "
        f"{structure_hint} "
        "세부 의미 해석은 하지 않았고, 이 설명은 제목과 파일 트리만으로 추론했습니다 "
        "(inferred from title and file tree only)."
    )


def enrich_summary(summary: DatasetSummary) -> DatasetSummary:
    summary.modality_guess = infer_modality(
        summary.title,
        [item.path for item in summary.files],
        summary.metadata_lines,
    )
    summary.category_guess = infer_category(
        summary.title,
        [item.path for item in summary.files],
        summary.metadata_lines,
    )
    summary.inferred_summary = build_inferred_summary(summary)
    return summary
