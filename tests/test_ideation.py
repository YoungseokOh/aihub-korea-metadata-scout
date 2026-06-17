from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

from aihub_korea_metadata_scout.config import ScoutSettings
from aihub_korea_metadata_scout.llm.base import (
    LLMConfigurationError,
    LLMProvider,
    extract_json_object,
)
from aihub_korea_metadata_scout.llm.factory import build_provider, resolve_provider_name
from aihub_korea_metadata_scout.models import DatasetSummary
from aihub_korea_metadata_scout.pipeline.ideate import ideate_dataset
from aihub_korea_metadata_scout.pipeline.rank_ideas import build_idea_ranking
from aihub_korea_metadata_scout.storage.json_store import load_ideation_results


def settings_for(tmp_path: Path, monkeypatch) -> ScoutSettings:
    # Settings fields use env-var aliases, so route writes to tmp via the environment
    # (passing output_dir= as a kwarg is ignored by pydantic-settings aliases).
    monkeypatch.setenv("AIHUB_OUTPUT_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("AIHUB_CACHE_DIR", str(tmp_path / "data" / "raw"))
    return ScoutSettings()


def make_summary(dataset_key: int, title: str) -> DatasetSummary:
    return DatasetSummary(
        dataset_key=dataset_key,
        title=title,
        raw_title=title,
        tags=["ocr/document", "번호판"],
        category_guess="ocr/document",
        modality_guess="image",
        file_count=12,
        total_size_bytes=2048,
        human_size="2.0 KB",
        sample_file_paths=[f"{title}/01.데이터/train.zip"],
        metadata_lines=["원천데이터 추가개방"],
        source_command=f"aihubshell -mode l -datasetkey {dataset_key}",
        collected_at=datetime(2026, 3, 17, 3, 0, 0, tzinfo=UTC),
        parse_status="success",
        inferred_summary="메타데이터 기반 요약입니다.",
        opportunity_score=7,
        difficulty_score=5,
        data_readiness_score=6,
    )


class StubProvider(LLMProvider):
    name = "stub"

    def __init__(self, payload: dict, *, model: str = "stub-model") -> None:
        super().__init__(model=model)
        self.payload = payload
        self.calls: list[dict[str, str]] = []

    def complete_json(self, *, system: str, user: str) -> dict:
        self.calls.append({"system": system, "user": user})
        return self.payload


def sample_payload(*, best_name: str = "문서 검색 SaaS") -> dict:
    return {
        "overall_verdict": "메타데이터 기준으로는 OCR 자동화 제품에 적합해 보입니다.",
        "notes": ["라이선스는 별도 확인 필요"],
        "ideas": [
            {
                "name": best_name,
                "one_liner": "공공 문서를 검색 가능한 형태로 변환",
                "app_or_web": "web",
                "target_users": ["공공기관", "백오피스 팀"],
                "core_features": ["OCR 인입", "전문 검색"],
                "data_usage": "문서 OCR 라벨로 검색 모델을 학습",
                "mvp_flow": ["문서 업로드", "OCR 처리", "검색 UI"],
                "monetization": ["엔터프라이즈 구독"],
                "inference_note": "서버 추론, 사전학습 모델 파인튜닝",
                "solo_feasibility": "B2B라 솔로엔 영업 부담",
                "differentiation": "공공행정 도메인 특화",
                "feasibility": "go",
                "opportunity_score": 9,
                "feasibility_score": 7,
                "data_fit_score": 8,
                "risks": ["라벨 품질 미확인"],
            },
            {
                "name": "모바일 스캐너",
                "one_liner": "현장에서 문서를 찍어 분류",
                "app_or_web": "app",
                "target_users": ["현장 직원"],
                "core_features": ["촬영", "자동 분류"],
                "data_usage": "분류 라벨 활용",
                "mvp_flow": ["촬영", "분류", "저장"],
                "monetization": ["IAP"],
                "inference_note": "온디바이스 분류 가능",
                "solo_feasibility": "혼자 출시 가능",
                "differentiation": "현장 특화 UX",
                "feasibility": "maybe",
                "opportunity_score": 6,
                "feasibility_score": 5,
                "data_fit_score": 6,
                "risks": ["현장 환경 편차"],
            },
        ],
    }


def test_extract_json_object_handles_code_fences() -> None:
    text = '```json\n{"overall_verdict": "ok", "notes": [], "ideas": []}\n```'
    parsed = extract_json_object(text)
    assert parsed["overall_verdict"] == "ok"


def test_extract_json_object_handles_surrounding_prose() -> None:
    text = '판정 결과입니다: {"overall_verdict": "ok", "notes": [], "ideas": []} 끝.'
    parsed = extract_json_object(text)
    assert parsed["ideas"] == []


def test_ideate_dataset_persists_json_and_markdown(tmp_path: Path, monkeypatch) -> None:
    settings = settings_for(tmp_path, monkeypatch)
    settings.ensure_directories()
    summary = make_summary(88, "공공행정문서 OCR")
    provider = StubProvider(sample_payload())

    result = ideate_dataset(settings, summary, provider, max_ideas=5)

    assert result.dataset_key == 88
    assert result.provider == "stub"
    assert result.idea_count == 2
    assert result.go_idea_count == 1
    # Best idea is ranked by combined score (opportunity-weighted).
    assert result.best_idea is not None
    assert result.best_idea.name == "문서 검색 SaaS"
    assert provider.calls and "공공행정문서 OCR" in provider.calls[0]["user"]

    json_path = Path(result.normalized_output_path)
    markdown_path = Path(result.markdown_output_path)
    assert json_path.exists()
    assert markdown_path.exists()
    # Richer per-idea fields flow through to the model and the rendered brief.
    best = result.best_idea
    assert best.mvp_flow and best.monetization
    assert best.inference_note and best.differentiation

    body = markdown_path.read_text(encoding="utf-8")
    assert "문서 검색 SaaS" in body
    assert "메타데이터" in body
    assert "MVP 흐름" in body
    assert "차별화 무기" in body


def test_ideate_dataset_clamps_out_of_range_scores(tmp_path: Path, monkeypatch) -> None:
    settings = settings_for(tmp_path, monkeypatch)
    settings.ensure_directories()
    summary = make_summary(90, "테스트 데이터")
    payload = {
        "overall_verdict": "v",
        "notes": [],
        "ideas": [
            {
                "name": "x",
                "one_liner": "y",
                "app_or_web": "unknown-surface",
                "target_users": [],
                "core_features": [],
                "data_usage": "",
                "feasibility": "weird",
                "opportunity_score": 99,
                "feasibility_score": -3,
                "data_fit_score": "n/a",
                "risks": [],
            }
        ],
    }
    result = ideate_dataset(settings, summary, StubProvider(payload), max_ideas=5)
    idea = result.ideas[0]
    assert idea.app_or_web == "both"
    assert idea.feasibility == "maybe"
    assert idea.opportunity_score == 10
    assert idea.feasibility_score == 1
    assert idea.data_fit_score == 5


def test_build_idea_ranking_orders_by_best_idea(tmp_path: Path, monkeypatch) -> None:
    settings = settings_for(tmp_path, monkeypatch)
    settings.ensure_directories()
    ideate_dataset(
        settings, make_summary(1, "약한 데이터"), StubProvider(sample_payload(best_name="약한 앱"))
    )
    # Second dataset with stronger scores should rank first.
    strong = sample_payload(best_name="강한 앱")
    strong["ideas"][0]["opportunity_score"] = 10
    strong["ideas"][0]["feasibility_score"] = 9
    ideate_dataset(settings, make_summary(2, "강한 데이터"), StubProvider(strong))

    markdown_path, json_path = build_idea_ranking(settings)
    assert markdown_path.exists()
    assert json_path.exists()

    results = load_ideation_results(settings)
    assert len(results) == 2
    body = markdown_path.read_text(encoding="utf-8")
    assert "강한 앱" in body
    # The strong dataset (key 2) should appear before the weak one (key 1).
    assert body.index("강한 데이터") < body.index("약한 데이터")


def test_user_prompt_enforces_minimum_five_ideas() -> None:
    from aihub_korea_metadata_scout.llm.prompts import build_user_prompt

    summary = make_summary(7, "테스트")
    # Even when asked for fewer, the prompt floors the target at 5.
    prompt = build_user_prompt(summary, max_ideas=2)
    assert "최소 5개" in prompt
    assert "MVP" in prompt


def test_resolve_provider_name_aliases() -> None:
    assert resolve_provider_name("claude") == "anthropic"
    assert resolve_provider_name("codex") == "openai"
    assert resolve_provider_name("LM-Studio") == "lmstudio"
    assert resolve_provider_name(None) == "lmstudio"
    with pytest.raises(LLMConfigurationError):
        resolve_provider_name("nonexistent")


def test_build_provider_missing_dependency_is_friendly(tmp_path: Path, monkeypatch) -> None:
    # Force the optional import to fail and assert we raise a helpful config error.
    import builtins

    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "openai":
            raise ImportError("no openai")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    settings = settings_for(tmp_path, monkeypatch)
    with pytest.raises(LLMConfigurationError):
        build_provider(settings, provider="lmstudio")
