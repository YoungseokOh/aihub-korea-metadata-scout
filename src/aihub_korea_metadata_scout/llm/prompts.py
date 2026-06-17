from __future__ import annotations

import json

from aihub_korea_metadata_scout.models import DatasetSummary

SYSTEM_PROMPT = """\
You are a pragmatic product strategist helping a solo builder decide whether an
AI-Hub Korea dataset could power a viable app or web product.

You ONLY receive metadata: a title, inferred tags, a file tree, file sizes, and
heuristic notes. You never see the actual data contents. Reason strictly from
this metadata and be explicit that every judgement is a metadata-only estimate.

For the given dataset, produce a short set of concrete app/web product ideas.
For each idea provide:
- name and a one-line pitch
- whether it fits an app, a web product, or both (app_or_web)
- target users and a few core features
- data_usage: why THIS dataset is needed for the idea
- a feasibility verdict: "go", "maybe", or "no-go"
- three 1-10 scores: opportunity_score (market pull), feasibility_score (how
  buildable by a small team), data_fit_score (how well the dataset matches)
- key risks

Then give an overall_verdict (2-3 sentences) and a few notes.

Rules:
- Be honest. If the metadata is too thin or the data looks unfit, say "no-go".
- Do not invent labels, licenses, or contents you cannot see in the metadata.
- Respond ONLY with a JSON object matching the requested schema. No prose, no
  code fences. Write idea text in Korean; keep enum values exactly as specified
  (app/web/both, go/maybe/no-go).
"""


def _dataset_context(summary: DatasetSummary, *, max_ideas: int) -> dict[str, object]:
    return {
        "dataset_key": summary.dataset_key,
        "title": summary.title,
        "category_guess": summary.category_guess,
        "modality_guess": summary.modality_guess,
        "tags": summary.tags[:16],
        "file_count": summary.file_count,
        "human_size": summary.human_size,
        "sample_file_paths": summary.sample_file_paths[:12],
        "metadata_lines": summary.metadata_lines[:12],
        "notices": summary.notices[:6],
        "parse_status": summary.parse_status,
        "heuristic_inferred_summary": summary.inferred_summary,
        "heuristic_opportunity_score": summary.opportunity_score,
        "heuristic_difficulty_score": summary.difficulty_score,
        "heuristic_data_readiness_score": summary.data_readiness_score,
        "requested_idea_count": max_ideas,
    }


def build_user_prompt(summary: DatasetSummary, *, max_ideas: int = 5) -> str:
    context = _dataset_context(summary, max_ideas=max_ideas)
    context_json = json.dumps(context, ensure_ascii=False, indent=2)
    return (
        f"다음은 AI-Hub 데이터셋의 메타데이터입니다. 이 정보만으로 앱/웹 제품 아이디어를 "
        f"최대 {max_ideas}개 제안하고, 각 아이디어의 실현가능성을 판정/점수화하세요.\n\n"
        f"메타데이터(JSON):\n{context_json}\n\n"
        "요청한 JSON 스키마에 맞는 객체만 반환하세요."
    )
