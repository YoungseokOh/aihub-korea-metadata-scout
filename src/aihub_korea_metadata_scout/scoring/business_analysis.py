from __future__ import annotations

from aihub_korea_metadata_scout.models import BusinessOpportunity, DatasetSummary
from aihub_korea_metadata_scout.scoring.heuristics import enrich_summary, summarize_structure


def _clamp_score(value: int) -> int:
    return max(1, min(10, value))


def _contains_any(text: str, values: tuple[str, ...]) -> bool:
    lowered = text.casefold()
    return any(value.casefold() in lowered for value in values)


def _all_text(summary: DatasetSummary) -> str:
    parts = [summary.title, summary.category_guess or "", summary.modality_guess or ""]
    parts.extend(summary.sample_file_paths)
    return " ".join(parts)


def _business_use_cases(summary: DatasetSummary) -> list[str]:
    text = _all_text(summary)
    if _contains_any(text, ("ocr/document", "ocr", "문서", "공공행정")):
        return [
            "문서 인입 자동화 및 검색 보조",
            "공공기관 기록물 분류/검수 워크플로우",
            "규정 문서 추출형 B2B SaaS",
        ]
    if _contains_any(text, ("speech", "음성", "대화", "콜센터", "상담")):
        return [
            "콜센터 품질 분석",
            "음성 상담 요약 및 QA 도우미",
            "도메인 특화 음성 평가 벤치마크",
        ]
    if _contains_any(text, ("medical", "의학", "x-ray", "피부", "종양")):
        return [
            "의료 영상 보조 판독 도구",
            "전문의용 검색/평가 데이터셋",
            "의료 AI 모델 검증 파이프라인",
        ]
    if _contains_any(text, ("agriculture", "양식장", "농장", "반려견")):
        return [
            "농장/양식장 운영 모니터링",
            "현장 리포팅 자동화",
            "수직 도메인 분석 SaaS",
        ]
    if _contains_any(text, ("education", "교과", "문제", "교육")):
        return [
            "학습 보조 및 평가용 콘텐츠 생성",
            "교과 문제 풀이 도우미",
            "교육용 평가 벤치마크",
        ]
    return [
        "내부 데이터 파이프라인 실험",
        "도메인 특화 검색/분류 모델 평가",
        "수직형 AI 제품의 초기 검증셋",
    ]


def _customer_segments(summary: DatasetSummary) -> list[str]:
    text = _all_text(summary)
    if _contains_any(text, ("ocr", "문서", "공공행정", "법률")):
        return ["공공기관", "문서 자동화 SaaS 팀", "엔터프라이즈 백오피스 운영팀"]
    if _contains_any(text, ("음성", "대화", "콜센터", "상담")):
        return ["컨택센터 운영팀", "음성 분석 SaaS 팀", "고객지원 플랫폼 팀"]
    if _contains_any(text, ("의학", "x-ray", "피부", "종양")):
        return ["의료 AI 스타트업", "병원 연구조직", "헬스케어 소프트웨어 팀"]
    if _contains_any(text, ("교육", "교과", "문제")):
        return ["에듀테크 팀", "평가 콘텐츠 제작사", "학습도구 SaaS 팀"]
    if _contains_any(text, ("양식장", "농장", "로봇", "물류", "작전")):
        return ["산업 운영팀", "현장 자동화 벤더", "도메인 특화 솔루션 SI 팀"]
    return ["수직형 AI 제품팀", "데이터 중심 스타트업", "내부 분석 플랫폼 팀"]


def _monetization_models(summary: DatasetSummary) -> list[str]:
    text = _all_text(summary)
    if _contains_any(text, ("공공행정", "문서", "법률", "의학")):
        return ["엔터프라이즈 구독", "프로젝트 구축/커스터마이징", "검수 워크플로우 사용량 과금"]
    if _contains_any(text, ("음성", "대화", "콜센터")):
        return ["좌석 기반 SaaS", "통화량 기반 사용량 과금", "평가 리포트 패키지"]
    if _contains_any(text, ("교육", "교과")):
        return ["기관 구독", "API 사용량 과금", "콘텐츠 라이선스 패키지"]
    return ["월 구독", "사용량 과금 API", "전문 서비스 결합 판매"]


def _risks(summary: DatasetSummary) -> list[str]:
    risks = [
        "실제 라이선스, 승인 범위, 정책 제약은 별도 검증이 필요합니다.",
        "메타데이터만으로는 라벨 품질과 결측 비율을 확인할 수 없습니다.",
    ]
    if summary.file_count >= 20:
        risks.append(
            "압축 조각 수가 많아 사전 정리 자동화 없이는 운영 복잡도가 올라갈 수 있습니다."
        )
    if summary.total_size_bytes and summary.total_size_bytes >= 50 * 1024**3:
        risks.append(
            "대용량 데이터는 저장비와 전처리 시간이 초기 사업 실험 속도를 늦출 수 있습니다."
        )
    if summary.parse_status != "success":
        risks.append("파싱이 부분 성공 상태라 실제 구조를 다시 확인해야 할 수 있습니다.")
    return risks


def _practicality(summary: DatasetSummary, difficulty_score: int) -> list[str]:
    items = summarize_structure(summary)
    if difficulty_score >= 8:
        items.append("실사용 전까지 저장소/배치 처리 설계를 먼저 잡는 편이 안전해 보입니다.")
    elif difficulty_score <= 4:
        items.append("작은 범위의 MVP 검증에는 비교적 빠르게 투입할 수 있어 보입니다.")
    else:
        items.append(
            "전처리 자동화가 있으면 시범 적용은 가능하지만 "
            "운영화까지는 추가 정리가 필요해 보입니다."
        )
    items.append("법률·정책 적합성은 별도 확인이 필요합니다.")
    return items


def build_business_opportunity(summary: DatasetSummary) -> BusinessOpportunity:
    summary = enrich_summary(summary)

    opportunity = 5
    difficulty = 3
    readiness = 5
    reasons: list[str] = []

    if summary.category_guess in {"ocr/document", "speech/dialogue", "medical", "education"}:
        opportunity += 2
        reasons.append("상업적 수요가 반복적으로 발생하는 문제 영역으로 보입니다.")
    if summary.category_guess in {"agriculture/aquaculture", "robotics", "industrial/operations"}:
        opportunity += 1
        reasons.append("도메인 특화 데이터라 차별화 포인트가 있을 수 있습니다.")
    if summary.modality_guess == "multimodal":
        opportunity += 1
        difficulty += 2
        reasons.append("멀티모달 구조는 활용 범위가 넓지만 구현 난도가 올라갑니다.")
    if summary.modality_guess in {"video", "3d/lidar"}:
        difficulty += 2
        opportunity -= 1
        reasons.append("영상/3D 계열은 저장·전처리·서빙 부담이 큰 편입니다.")
    if summary.total_size_bytes:
        if summary.total_size_bytes >= 100 * 1024**3:
            difficulty += 3
            opportunity -= 1
            reasons.append("표시된 용량이 매우 커서 초기 실험 비용이 큽니다.")
        elif summary.total_size_bytes >= 10 * 1024**3:
            difficulty += 2
            reasons.append("수십 GB 규모라 로컬 처리 부담이 있습니다.")
        elif summary.total_size_bytes >= 1 * 1024**3:
            difficulty += 1
            reasons.append("수 GB급 데이터라 기본 저장 공간 계획이 필요합니다.")
        else:
            opportunity += 1
            reasons.append("상대적으로 작은 규모라 빠른 MVP 검증에 유리해 보입니다.")
    if summary.file_count >= 20:
        difficulty += 2
        readiness -= 1
        reasons.append("압축 조각이 많아 전처리 파이프라인이 필요해 보입니다.")
    elif 1 <= summary.file_count <= 6:
        readiness += 1
        reasons.append("파일 구조가 단순해 보여 구조 파악이 쉽습니다.")
    if any("라벨" in path or "label" in path.casefold() for path in summary.sample_file_paths):
        readiness += 1
        reasons.append("라벨링 데이터가 보여 활용 가설을 세우기 쉽습니다.")
    if any("training" in path.casefold() for path in summary.sample_file_paths) and any(
        "validation" in path.casefold() for path in summary.sample_file_paths
    ):
        readiness += 1
        reasons.append("학습/검증 분리가 보입니다.")
    if summary.parse_status != "success":
        readiness -= 2
        reasons.append("파싱이 부분 성공이어서 구조 신뢰도를 보수적으로 잡아야 합니다.")
    if not summary.files:
        opportunity -= 2
        difficulty += 2
        readiness -= 3
        reasons.append("파일 정보가 거의 없어 사업성과 활용 난도를 판단하기 어렵습니다.")

    opportunity_score = _clamp_score(opportunity)
    difficulty_score = _clamp_score(difficulty)
    data_readiness_score = _clamp_score(readiness)

    why_interesting = [
        "메타데이터만 봐도 활용 장면이 비교적 선명하게 떠오르는 편입니다."
        if opportunity_score >= 7
        else "좁은 문제를 빠르게 실험하는 데는 의미가 있을 수 있습니다.",
        "구조가 드러난 파일 트리는 초기 타당성 검토 속도를 높여 줍니다.",
    ]
    why_it_might_fail = [
        "실제 내용 품질이 기대보다 낮으면 사업화 가정이 쉽게 무너질 수 있습니다.",
        "메타데이터 기반 해석이라 현업 니즈와 어긋날 가능성을 열어 둬야 합니다.",
    ]

    return BusinessOpportunity(
        inferred_summary=summary.inferred_summary,
        business_use_cases=_business_use_cases(summary),
        customer_segments=_customer_segments(summary),
        monetization_models=_monetization_models(summary),
        risks=_risks(summary),
        why_interesting=why_interesting,
        why_it_might_fail=why_it_might_fail,
        practicality_assessment=_practicality(summary, difficulty_score),
        opportunity_score=opportunity_score,
        difficulty_score=difficulty_score,
        data_readiness_score=data_readiness_score,
        score_reasons=reasons,
    )


def apply_business_analysis(summary: DatasetSummary) -> DatasetSummary:
    opportunity = build_business_opportunity(summary)
    summary.inferred_summary = opportunity.inferred_summary
    summary.business_use_cases = opportunity.business_use_cases
    summary.customer_segments = opportunity.customer_segments
    summary.monetization_models = opportunity.monetization_models
    summary.risks = opportunity.risks
    summary.difficulty_score = opportunity.difficulty_score
    summary.opportunity_score = opportunity.opportunity_score
    summary.data_readiness_score = opportunity.data_readiness_score
    summary.score_reasons = opportunity.score_reasons
    summary.business_opportunity = opportunity
    return summary
