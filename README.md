# Am I scooped?

A research-overlap skill for Codex. It uses the current model's web search and native subagents to find competing work, inspect decisive source passages, and judge whether the actual contribution has already been covered.

**直接联网检索，核对原文，明确判断研究是否被抢先。**

## What you get

| Verdict | Meaning |
|---|---|
| 目前安全 / Safe | The central contribution remains distinct in the assessed scope. |
| 已有风险 / At risk | Prior work threatens an independently claimed contribution, while another substantive contribution survives. |
| 几乎已被 scoop / Substantially scooped | Public technical evidence already covers the central contribution at equivalent or broader scope. |

The result includes a concise in-chat decision, claim-by-claim evidence, source links and dates, a concrete recommendation, and a standalone HTML report. The report records the actual search scope and queries. If essential evidence cannot be retrieved, the assessment is explicitly unfinished rather than assigned a reassuring label.

The skill distinguishes a new result from a shared method, an integrated contribution from its known ingredients, and a general result from an already solved special case. It checks the version containing the relevant result when publication order matters.

## Install

Clone this repository into your personal Codex skills directory:

```bash
skills_root="${CODEX_HOME:-$HOME/.codex}/skills"
mkdir -p "$skills_root"
git clone https://github.com/Alice-Shimada/am-i-scooped.git "$skills_root/am-i-scooped"
```

The directory should contain `SKILL.md` at its root. This command installs into a new directory; an existing installation is not overwritten.

## Use

```text
$am-i-scooped
判断以下研究想法是否被抢先：……
我的核心贡献是……；已有背景方法是……。
```

Or:

```text
$am-i-scooped
Compare my proposed result with this paper: …
The new contribution I claim is …
```

You can supply an idea, manuscript, project description, or competing paper. State a historical cutoff or a particular competitor when that is the question you want assessed. Without a date restriction, the skill searches prior literature through the assessment date.

## Runtime

- A host with model reasoning, web search, and source-reading tools. Native subagents are used when available and useful.
- Python 3 to render the HTML report. The renderer uses only the standard library and runs offline.
- No separate model API client, search-service key, crawler, database, or application server.

Accuracy takes priority over latency. Straightforward search and bibliographic tasks may use lower subagent reasoning effort. **The skill must never autonomously enable fast mode or change its settings.**

## Files

- [SKILL.md](SKILL.md): workflow and verdict rules.
- [references/judgment.md](references/judgment.md): claim comparison, chronology, and false-alarm handling.
- [references/report-format.md](references/report-format.md): report data format.
- [scripts/render_report.py](scripts/render_report.py): offline report renderer.
- [assets/report-template.html](assets/report-template.html): responsive report template.
- [agents/openai.yaml](agents/openai.yaml): skill display metadata.

To render an assessment prepared by the skill:

```bash
python3 scripts/render_report.py /path/to/report.json --output /path/to/report.html
```

Use a new output filename for each report or revision. The renderer checks report consistency and formats supplied judgments; it does not search the web or decide scientific novelty.
