#!/usr/bin/env python3
"""Render an am-i-scooped JSON assessment as one offline HTML file."""

import argparse
import html
import json
from pathlib import Path
from string import Template
from urllib.parse import urlsplit


VERDICTS = ("safe", "risk", "scooped")
BASES = ("novelty", "public_priority")
EVIDENCE = ("metadata", "abstract", "selected_full_text", "full_text", "released_artifact", "user_excerpt")
LANGUAGES = ("en", "zh-CN")
LABELS = {
    "en": {
        "safe": "Currently safe", "risk": "At risk", "scooped": "Substantially scooped",
        "novelty": "Current novelty", "public_priority": "Public priority",
        "metadata": "Metadata only", "abstract": "Abstract read",
        "selected_full_text": "Relevant passages read", "full_text": "Full text read",
        "released_artifact": "Released artifact checked", "user_excerpt": "User-provided excerpt",
        "edition": "Research priority · Contribution overlap",
        "assessment_label": "Assessment outcome", "action_label": "What to do now",
        "basis_label": "Assessment basis", "assessed_at_label": "Assessed on",
        "scope_label": "Search and assessment scope",
        "claims_heading": "Claim-by-claim assessment", "claims_note": "Central claims are marked",
        "sources_heading": "Decisive sources and findings", "source_count_label": "Sources recorded: {count}",
        "next_heading": "Next steps", "query_count_label": "Search log · Queries: {count}",
        "unlinked": "None linked", "central_claim": "Central claim", "other_claim": "Other claim",
        "sources_label": "Sources", "claim_column": "Contribution claim",
        "verdict_column": "Verdict", "reason_column": "Reasoning",
        "no_claims": "No assessable claims recorded.", "no_excerpt": "No verbatim excerpt included.",
        "date_label": "Date", "version_label": "Version", "not_recorded": "Not recorded",
        "evidence_details": "Inspect evidence and differences", "locator_label": "Evidence location",
        "difference_label": "Difference from the proposed work", "excerpt_label": "Source excerpt",
        "linked_claims": "Linked claims", "query_column": "Search query",
        "purpose_column": "Purpose", "result_column": "Actual result",
        "no_queries": "No search queries recorded.", "blockers_heading": "Current blockers and search gaps",
        "gaps_heading": "Search gaps", "milestone_label": "Your public milestone",
        "incomplete_outcome": "Search incomplete", "incomplete_status": "Search status · Incomplete",
        "complete_status": "Search status · Assessment complete",
        "no_sources": "No sources available to record.", "no_next_steps": "No additional steps recorded.",
    },
    "zh-CN": {
        "safe": "目前安全", "risk": "已有风险", "scooped": "几乎已被 scoop",
        "novelty": "当前新颖性", "public_priority": "公开优先顺序",
        "metadata": "仅元数据", "abstract": "已读摘要",
        "selected_full_text": "已读相关正文段落", "full_text": "已读全文",
        "released_artifact": "已核对发布产物", "user_excerpt": "用户提供摘录",
        "edition": "文献优先权 · 贡献重叠评估",
        "assessment_label": "评估结论", "action_label": "现在做什么",
        "basis_label": "评估口径", "assessed_at_label": "评估时间",
        "scope_label": "本次检索与判断范围",
        "claims_heading": "逐项贡献判断", "claims_note": "核心主张已单独标记",
        "sources_heading": "决定性来源与发现", "source_count_label": "{count} 条已登记来源",
        "next_heading": "下一步", "query_count_label": "检索记录 · {count} 条检索式",
        "unlinked": "未关联", "central_claim": "核心主张", "other_claim": "其他主张",
        "sources_label": "来源", "claim_column": "贡献主张",
        "verdict_column": "判断", "reason_column": "依据",
        "no_claims": "尚未登记可评估的贡献主张。", "no_excerpt": "未附逐字摘录。",
        "date_label": "日期", "version_label": "版本", "not_recorded": "未记录",
        "evidence_details": "核对证据与差异", "locator_label": "证据位置",
        "difference_label": "与当前工作的差异", "excerpt_label": "原文摘录",
        "linked_claims": "关联主张", "query_column": "检索式",
        "purpose_column": "目的", "result_column": "实际结果",
        "no_queries": "尚无已记录的检索式。", "blockers_heading": "当前阻碍与检索缺口",
        "gaps_heading": "检索缺口", "milestone_label": "用户公开时间节点",
        "incomplete_outcome": "检索未完成", "incomplete_status": "检索状态 · 未完成",
        "complete_status": "检索状态 · 已完成本轮检索",
        "no_sources": "尚未取得可登记的来源。", "no_next_steps": "未记录额外步骤。",
    },
}


def escape(value):
    return html.escape(str(value), quote=True)


def require_text(item, key, where, nonempty=True):
    value = item.get(key)
    if not isinstance(value, str) or (nonempty and not value.strip()):
        raise ValueError(f"{where}.{key} must be {'a nonempty' if nonempty else 'a'} string")


def require_list(item, key, where):
    if not isinstance(item.get(key), list):
        raise ValueError(f"{where}.{key} must be an array")
    return item[key]


def validate(data):
    """Check the report contract, without deriving any scientific verdict."""
    if not isinstance(data, dict):
        raise ValueError("report must be an object")
    if "language" in data and data["language"] not in LANGUAGES:
        raise ValueError("language must be en or zh-CN")
    for key in ("title", "assessed_at", "scope", "summary", "recommendation"):
        require_text(data, key, "report")
    if data.get("basis") not in tuple(BASES):
        raise ValueError("basis must be novelty or public_priority")
    status, verdict = data.get("status"), data.get("verdict")
    if status not in ("complete", "incomplete"):
        raise ValueError("status must be complete or incomplete")
    if status == "complete" and verdict not in tuple(VERDICTS):
        raise ValueError("a complete report needs verdict safe, risk, or scooped")
    if status == "incomplete" and ("verdict" not in data or verdict is not None):
        raise ValueError("an incomplete report needs verdict=null")
    milestone = data.get("user_milestone")
    if milestone is not None:
        if not isinstance(milestone, dict):
            raise ValueError("user_milestone must be an object or null")
        for key in ("date", "url", "description"):
            require_text(milestone, key, "user_milestone")
    if status == "complete" and data["basis"] == "public_priority" and milestone is None:
        raise ValueError("a complete public_priority report needs user_milestone")
    if status == "complete" and data["basis"] == "public_priority" and not usable_url(milestone["url"]):
        raise ValueError("a complete public_priority report needs a usable public milestone URL")

    claims = require_list(data, "claims", "report")
    sources = require_list(data, "sources", "report")
    id_sets = {}
    for kind, items, text_fields in (
        ("claims", claims, ("id", "text", "reason")),
        ("sources", sources, ("id", "title", "finding")),
    ):
        ids = set()
        for index, item in enumerate(items):
            where = f"{kind}[{index}]"
            if not isinstance(item, dict):
                raise ValueError(f"{where} must be an object")
            for key in text_fields:
                require_text(item, key, where)
            if item["id"] in ids:
                raise ValueError(f"duplicate {kind} id: {item['id']}")
            ids.add(item["id"])
            if kind == "claims":
                if type(item.get("central")) is not bool:
                    raise ValueError(f"{where}.central must be boolean")
                if item.get("verdict") not in tuple(VERDICTS):
                    raise ValueError(f"{where}.verdict must be safe, risk, or scooped")
            else:
                for key in ("url", "date", "version", "locator", "difference"):
                    require_text(item, key, where, nonempty=False)
                if item.get("evidence_level") not in tuple(EVIDENCE):
                    raise ValueError(f"{where}.evidence_level is not recognized")
                if "excerpt" in item:
                    require_text(item, "excerpt", where, nonempty=False)
        id_sets[kind] = ids

    for kind, items, key, target in (
        ("claims", claims, "source_ids", "sources"),
        ("sources", sources, "claim_ids", "claims"),
    ):
        for index, item in enumerate(items):
            where = f"{kind}[{index}]"
            for ref in require_list(item, key, where):
                if not isinstance(ref, str) or ref not in id_sets[target]:
                    raise ValueError(f"{where}.{key} contains an unknown {target} id: {ref}")

    claim_links = {(claim["id"], source_id) for claim in claims for source_id in claim["source_ids"]}
    source_links = {(claim_id, source["id"]) for source in sources for claim_id in source["claim_ids"]}
    if claim_links != source_links:
        raise ValueError("claim source_ids and source claim_ids must agree in both directions")
    sources_by_id = {source["id"]: source for source in sources}
    for claim in claims:
        if claim["verdict"] in ("risk", "scooped") and not claim["source_ids"]:
            raise ValueError(f"claim {claim['id']} needs sources for verdict {claim['verdict']}")
        if claim["verdict"] == "risk" and not any(
            source["evidence_level"] in ("abstract", "selected_full_text", "full_text", "released_artifact")
            and usable_url(source["url"])
            for source in (sources_by_id[source_id] for source_id in claim["source_ids"])
        ):
            raise ValueError(f"risk claim {claim['id']} needs public evidence with a usable HTTP(S) URL")
        if claim["verdict"] == "scooped" and not any(
            source["evidence_level"] in ("selected_full_text", "full_text", "released_artifact")
            and usable_url(source["url"])
            and all(source[key].strip() for key in ("date", "version", "locator"))
            for source in (sources_by_id[source_id] for source_id in claim["source_ids"])
        ):
            raise ValueError(f"scooped claim {claim['id']} needs technical evidence with a usable HTTP(S) URL, date, version, and locator")

    coverage = data.get("coverage")
    if not isinstance(coverage, dict):
        raise ValueError("coverage must be an object")
    for index, query in enumerate(require_list(coverage, "queries", "coverage")):
        if not isinstance(query, dict):
            raise ValueError(f"coverage.queries[{index}] must be an object")
        for key in ("query", "purpose", "result"):
            require_text(query, key, f"coverage.queries[{index}]")
    for item, key, where in ((coverage, "gaps", "coverage"), (data, "next_steps", "report")):
        values = require_list(item, key, where)
        if any(not isinstance(value, str) or not value.strip() for value in values):
            raise ValueError(f"{where}.{key} must contain nonempty strings")
    if status == "incomplete" and not coverage["gaps"]:
        raise ValueError("an incomplete report must record actual blockers in coverage.gaps")
    if status == "complete":
        central = [claim for claim in claims if claim["central"]]
        if not central:
            raise ValueError("a complete report needs at least one central claim")
        if not coverage["queries"]:
            raise ValueError("a complete report needs actual coverage.queries")
        central_verdicts = {claim["verdict"] for claim in central}
        expected = "safe" if central_verdicts == {"safe"} else "scooped" if central_verdicts == {"scooped"} else "risk"
        if verdict != expected:
            raise ValueError(f"overall {verdict} conflicts with central claims; expected {expected}")


def usable_url(url):
    try:
        parsed = urlsplit(url)
        return (
            parsed.scheme.lower() in ("http", "https")
            and bool(parsed.hostname)
            and not any(ord(char) <= 32 for char in url)
        )
    except ValueError:
        return False


def external_title(source):
    """Unsafe or absent URLs remain plain text; report rendering never fetches them."""
    url = source["url"]
    title = escape(source["title"])
    if usable_url(url):
        return f'<a href="{escape(url)}" rel="noopener noreferrer">{title}<span aria-hidden="true"> ↗</span></a>'
    return title


def badge(verdict, labels):
    return f'<span class="badge {verdict}">{labels[verdict]}</span>'


def item_list(values, empty):
    if not values:
        return f'<p class="muted">{escape(empty)}</p>'
    return '<ul class="plain-list">' + "".join(f"<li>{escape(value)}</li>" for value in values) + "</ul>"


def render(data, language=None):
    validate(data)
    language = data.get("language", "zh-CN") if language is None else language
    if language not in LANGUAGES:
        raise ValueError("language must be en or zh-CN")
    labels = LABELS[language]
    source_anchors = {source["id"]: f"source-{index}" for index, source in enumerate(data["sources"], 1)}
    claim_anchors = {claim["id"]: f"claim-{index}" for index, claim in enumerate(data["claims"], 1)}

    def references(ids, anchors):
        return " · ".join(f'<a href="#{anchors[ref]}">{escape(ref)}</a>' for ref in ids) or labels["unlinked"]

    claim_rows = []
    for claim in data["claims"]:
        central = f'<span class="central">{labels["central_claim"]}</span>' if claim["central"] else f'<span class="muted">{labels["other_claim"]}</span>'
        claim_rows.append(
            f'<tr id="{claim_anchors[claim["id"]]}"><th scope="row"><span class="record-id">{escape(claim["id"])}</span>'
            f'<p>{escape(claim["text"])}</p>{central}</th><td>{badge(claim["verdict"], labels)}</td>'
            f'<td><p>{escape(claim["reason"])}</p><div class="source-refs">{labels["sources_label"]}: {references(claim["source_ids"], source_anchors)}</div></td></tr>'
        )
    claims_html = (
        f'<div class="table-wrap"><table><thead><tr><th>{labels["claim_column"]}</th><th>{labels["verdict_column"]}</th><th>{labels["reason_column"]}</th></tr></thead><tbody>'
        + "".join(claim_rows) + "</tbody></table></div>"
        if claim_rows else f'<p class="muted">{labels["no_claims"]}</p>'
    )

    source_cards = []
    for source in data["sources"]:
        excerpt = f'<blockquote>{escape(source["excerpt"])}</blockquote>' if source.get("excerpt") else f'<p class="muted">{labels["no_excerpt"]}</p>'
        source_cards.append(
            f'<article class="source-card" id="{source_anchors[source["id"]]}">'
            f'<div class="source-heading"><span class="record-id">{escape(source["id"])}</span>'
            f'<span class="read-depth">{labels[source["evidence_level"]]}</span></div>'
            f'<h3>{external_title(source)}</h3><p class="source-meta">{labels["date_label"]}: {escape(source["date"] or labels["not_recorded"])}'
            f' <span aria-hidden="true">·</span> {labels["version_label"]}: {escape(source["version"] or labels["not_recorded"])}</p>'
            f'<p class="finding">{escape(source["finding"])}</p>'
            f'<details><summary>{labels["evidence_details"]}</summary><div class="detail-body">'
            f'<h4>{labels["locator_label"]}</h4><p>{escape(source["locator"] or labels["not_recorded"])}</p>'
            f'<h4>{labels["difference_label"]}</h4><p>{escape(source["difference"] or labels["not_recorded"])}</p>'
            f'<h4>{labels["excerpt_label"]}</h4>{excerpt}<p class="source-refs">{labels["linked_claims"]}: {references(source["claim_ids"], claim_anchors)}</p>'
            '</div></details></article>'
        )

    query_rows = "".join(
        f'<tr><th scope="row"><code>{escape(query["query"])}</code></th><td>{escape(query["purpose"])}</td><td>{escape(query["result"])}</td></tr>'
        for query in data["coverage"]["queries"]
    )
    queries_html = (
        f'<div class="table-wrap"><table class="query-table"><thead><tr><th>{labels["query_column"]}</th><th>{labels["purpose_column"]}</th><th>{labels["result_column"]}</th></tr></thead><tbody>'
        + query_rows + "</tbody></table></div>"
        if query_rows else f'<p class="muted">{labels["no_queries"]}</p>'
    )
    incomplete = data["status"] == "incomplete"
    state = "incomplete" if incomplete else data["verdict"]
    gaps = data["coverage"]["gaps"]
    gaps_title = labels["blockers_heading"] if incomplete else labels["gaps_heading"]
    gaps_panel = (
        f'<section class="note-panel gaps" aria-labelledby="gaps-title"><h2 id="gaps-title">{gaps_title}</h2>'
        + item_list(gaps, "") + "</section>" if gaps else ""
    )
    milestone = data.get("user_milestone")
    milestone_html = (
        f'<dl class="milestone"><dt>{labels["milestone_label"]}</dt><dd>'
        f'{escape(milestone["date"])}<br>'
        + external_title({"title": milestone["description"], "url": milestone["url"]})
        + "</dd></dl>" if milestone else ""
    )
    template = Template((Path(__file__).resolve().parent.parent / "assets" / "report-template.html").read_text(encoding="utf-8"))
    return template.substitute(
        labels, language=language,
        title=escape(data["title"]), assessed_at=escape(data["assessed_at"]), scope=escape(data["scope"]),
        basis=labels[data["basis"]], milestone=milestone_html,
        state=state, outcome=labels["incomplete_outcome"] if incomplete else labels[data["verdict"]],
        status_label=labels["incomplete_status"] if incomplete else labels["complete_status"],
        summary=escape(data["summary"]), recommendation=escape(data["recommendation"]),
        claims=claims_html, sources="".join(source_cards) or f'<p class="muted">{labels["no_sources"]}</p>',
        source_count_label=labels["source_count_label"].format(count=len(data["sources"])),
        query_count_label=labels["query_count_label"].format(count=len(data["coverage"]["queries"])), queries=queries_html,
        next_steps=item_list(data["next_steps"], labels["no_next_steps"]),
        gaps_panel=gaps_panel, bottom_class="" if gaps else " single",
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="assessment JSON file")
    parser.add_argument("--output", required=True, type=Path, help="standalone HTML output file")
    parser.add_argument("--language", choices=LANGUAGES, help="UI language; overrides JSON language (legacy default: zh-CN). Does not translate report prose.")
    args = parser.parse_args()
    try:
        if args.input.resolve() == args.output.resolve():
            raise ValueError("input and output must be different files")
        report = render(json.loads(args.input.read_text(encoding="utf-8")), language=args.language)
        with args.output.open("x", encoding="utf-8") as output:
            output.write(report)
    except (OSError, UnicodeError, ValueError) as error:
        parser.exit(2, f"error: {error}\n")
    print(args.output.resolve())


if __name__ == "__main__":
    main()
