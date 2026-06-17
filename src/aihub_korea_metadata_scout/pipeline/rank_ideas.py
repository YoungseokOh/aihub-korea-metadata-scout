from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from aihub_korea_metadata_scout.config import ScoutSettings
from aihub_korea_metadata_scout.models import IdeationResult
from aihub_korea_metadata_scout.storage.json_store import load_ideation_results, write_json
from aihub_korea_metadata_scout.storage.markdown_store import write_markdown


def _ranked(results: list[IdeationResult]) -> list[IdeationResult]:
    return sorted(
        results,
        key=lambda item: (item.ranking_score, item.go_idea_count),
        reverse=True,
    )


def _render_markdown(results: list[IdeationResult], generated_at: datetime) -> str:
    lines = [
        "# AI-Hub Korea 앱/웹 아이디어 랭킹",
        "",
        f"생성 시각: {generated_at.isoformat()}",
        "",
        "각 데이터셋의 LLM 아이디어 판정 결과를 대표 아이디어 점수(best idea combined) "
        "기준으로 정렬했습니다. 모든 점수는 메타데이터 기반 추정입니다.",
        "",
        "## 데이터셋별 요약",
        "",
        "| 순위 | Dataset | 대표 아이디어 | combined | go/총 | provider |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    ranked = _ranked(results)
    for index, result in enumerate(ranked, start=1):
        best = result.best_idea
        best_name = best.name if best is not None else "-"
        lines.append(
            f"| {index} | `{result.dataset_key}` {result.title} | {best_name} | "
            f"{result.ranking_score:.2f} | {result.go_idea_count}/{result.idea_count} | "
            f"`{result.provider}` |"
        )

    lines.extend(["", "## 상위 아이디어 상세", ""])
    for result in ranked[:10]:
        best = result.best_idea
        if best is None:
            continue
        lines.append(
            f"### `{result.dataset_key}` {result.title} → {best.name} "
            f"(`{best.feasibility}`, combined {best.combined_score:.2f})"
        )
        lines.append(f"- {best.one_liner}")
        lines.append(
            f"- 형태 `{best.app_or_web}` · 기회 {best.opportunity_score}/10 · "
            f"실현 {best.feasibility_score}/10 · 데이터 적합 {best.data_fit_score}/10"
        )
        if result.markdown_output_path:
            lines.append(f"- 상세 브리프: `{result.markdown_output_path}`")
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def build_idea_ranking(settings: ScoutSettings) -> tuple[Path, Path]:
    """Aggregate existing ideation JSON files into a ranked comparison catalog."""

    settings.ensure_directories()
    results = load_ideation_results(settings)
    generated_at = datetime.now(UTC)

    markdown_body = _render_markdown(results, generated_at)
    markdown_path = settings.idea_ranking_markdown_path
    write_markdown(markdown_path, markdown_body)

    ranked = _ranked(results)
    payload = {
        "generated_at": generated_at.isoformat(),
        "dataset_count": len(results),
        "ranking": [
            {
                "rank": index,
                "dataset_key": result.dataset_key,
                "title": result.title,
                "provider": result.provider,
                "model": result.model,
                "ranking_score": result.ranking_score,
                "idea_count": result.idea_count,
                "go_idea_count": result.go_idea_count,
                "best_idea": result.best_idea.name if result.best_idea else None,
                "best_idea_feasibility": (
                    result.best_idea.feasibility if result.best_idea else None
                ),
                "markdown_output_path": result.markdown_output_path,
            }
            for index, result in enumerate(ranked, start=1)
        ],
    }
    json_path = write_json(settings.idea_ranking_json_path, payload)
    return markdown_path, json_path
