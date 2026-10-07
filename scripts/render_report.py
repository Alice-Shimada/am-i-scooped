#!/usr/bin/env python3
"""Render an am-i-scooped JSON assessment as one offline HTML file."""

import argparse
import html
import json
from pathlib import Path
from string import Template
from urllib.parse import urlsplit


VERDICTS = {"safe": "目前安全", "risk": "已有风险", "scooped": "几乎已被 scoop"}
BASES = {"novelty": "当前新颖性", "public_priority": "公开优先顺序"}
EVIDENCE = {
    "metadata": "仅元数据",
    "abstract": "已读摘要",
    "selected_full_text": "已读相关正文段落",
    "full_text": "已读全文",
    "released_artifact": "已核对发布产物",
    "user_excerpt": "用户提供摘录",
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


def badge(verdict):
    return f'<span class="badge {verdict}">{VERDICTS[verdict]}</span>'


def item_list(values, empty):
    if not values:
        return f'<p class="muted">{escape(empty)}</p>'
    return '<ul class="plain-list">' + "".join(f"<li>{escape(value)}</li>" for value in values) + "</ul>"


def render(data):
    validate(data)
    source_anchors = {source["id"]: f"source-{index}" for index, source in enumerate(data["sources"], 1)}
    claim_anchors = {claim["id"]: f"claim-{index}" for index, claim in enumerate(data["claims"], 1)}

    def references(ids, anchors):
        return " · ".join(f'<a href="#{anchors[ref]}">{escape(ref)}</a>' for ref in ids) or "未关联"

    claim_rows = []
    for claim in data["claims"]:
        central = '<span class="central">核心主张</span>' if claim["central"] else '<span class="muted">其他主张</span>'
        claim_rows.append(
            f'<tr id="{claim_anchors[claim["id"]]}"><th scope="row"><span class="record-id">{escape(claim["id"])}</span>'
            f'<p>{escape(claim["text"])}</p>{central}</th><td>{badge(claim["verdict"])}</td>'
            f'<td><p>{escape(claim["reason"])}</p><div class="source-refs">来源：{references(claim["source_ids"], source_anchors)}</div></td></tr>'
        )
    claims_html = (
        '<div class="table-wrap"><table><thead><tr><th>贡献主张</th><th>判断</th><th>依据</th></tr></thead><tbody>'
        + "".join(claim_rows) + "</tbody></table></div>"
        if claim_rows else '<p class="muted">尚未登记可评估的贡献主张。</p>'
    )

    source_cards = []
    for source in data["sources"]:
        excerpt = f'<blockquote>{escape(source["excerpt"])}</blockquote>' if source.get("excerpt") else '<p class="muted">未附逐字摘录。</p>'
        source_cards.append(
            f'<article class="source-card" id="{source_anchors[source["id"]]}">'
            f'<div class="source-heading"><span class="record-id">{escape(source["id"])}</span>'
            f'<span class="read-depth">{EVIDENCE[source["evidence_level"]]}</span></div>'
            f'<h3>{external_title(source)}</h3><p class="source-meta">日期：{escape(source["date"] or "未记录")}'
            f' <span aria-hidden="true">·</span> 版本：{escape(source["version"] or "未记录")}</p>'
            f'<p class="finding">{escape(source["finding"])}</p>'
            '<details><summary>核对证据与差异</summary><div class="detail-body">'
            f'<h4>证据位置</h4><p>{escape(source["locator"] or "未记录")}</p>'
            f'<h4>与当前工作的差异</h4><p>{escape(source["difference"] or "未记录")}</p>'
            f'<h4>原文摘录</h4>{excerpt}<p class="source-refs">关联主张：{references(source["claim_ids"], claim_anchors)}</p>'
            '</div></details></article>'
        )

    query_rows = "".join(
        f'<tr><th scope="row"><code>{escape(query["query"])}</code></th><td>{escape(query["purpose"])}</td><td>{escape(query["result"])}</td></tr>'
        for query in data["coverage"]["queries"]
    )
    queries_html = (
        '<div class="table-wrap"><table class="query-table"><thead><tr><th>检索式</th><th>目的</th><th>实际结果</th></tr></thead><tbody>'
        + query_rows + "</tbody></table></div>"
        if query_rows else '<p class="muted">尚无已记录的检索式。</p>'
    )
    incomplete = data["status"] == "incomplete"
    state = "incomplete" if incomplete else data["verdict"]
    gaps = data["coverage"]["gaps"]
    gaps_title = "当前阻碍与检索缺口" if incomplete else "检索缺口"
    gaps_panel = (
        f'<section class="note-panel gaps" aria-labelledby="gaps-title"><h2 id="gaps-title">{gaps_title}</h2>'
        + item_list(gaps, "") + "</section>" if gaps else ""
    )
    milestone = data.get("user_milestone")
    milestone_html = (
        '<dl class="milestone"><dt>用户公开时间节点</dt><dd>'
        f'{escape(milestone["date"])}<br>'
        + external_title({"title": milestone["description"], "url": milestone["url"]})
        + "</dd></dl>" if milestone else ""
    )
    template = Template((Path(__file__).resolve().parent.parent / "assets" / "report-template.html").read_text(encoding="utf-8"))
    return template.substitute(
        title=escape(data["title"]), assessed_at=escape(data["assessed_at"]), scope=escape(data["scope"]),
        basis=BASES[data["basis"]], milestone=milestone_html,
        state=state, outcome="检索未完成" if incomplete else VERDICTS[data["verdict"]],
        status_label="检索状态 · 未完成" if incomplete else "检索状态 · 已完成本轮检索",
        summary=escape(data["summary"]), recommendation=escape(data["recommendation"]),
        claims=claims_html, sources="".join(source_cards) or '<p class="muted">尚未取得可登记的来源。</p>',
        source_count=len(data["sources"]), query_count=len(data["coverage"]["queries"]), queries=queries_html,
        next_steps=item_list(data["next_steps"], "未记录额外步骤。"),
        gaps_panel=gaps_panel, bottom_class="" if gaps else " single",
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="assessment JSON file")
    parser.add_argument("--output", required=True, type=Path, help="standalone HTML output file")
    args = parser.parse_args()
    try:
        if args.input.resolve() == args.output.resolve():
            raise ValueError("input and output must be different files")
        report = render(json.loads(args.input.read_text(encoding="utf-8")))
        with args.output.open("x", encoding="utf-8") as output:
            output.write(report)
    except (OSError, UnicodeError, ValueError) as error:
        parser.exit(2, f"error: {error}\n")
    print(args.output.resolve())


if __name__ == "__main__":
    main()
