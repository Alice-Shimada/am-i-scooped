# Report data and presentation

The analysis determines the verdict. The renderer formats the supplied data; it does not score papers or decide novelty. Use a self-contained UTF-8 JSON object with the following fields. The report supports English (`en`) and Simplified Chinese (`zh-CN`) throughout the interface.

```json
{
  "language": "en",
  "title": "A short name for the assessed contribution",
  "assessed_at": "2026-10-08 10:30 Asia/Shanghai",
  "scope": "The exact claims, date range, and domain searched",
  "basis": "novelty",
  "user_milestone": null,
  "status": "complete",
  "verdict": "risk",
  "summary": "One direct sentence naming the strongest reason for the verdict.",
  "recommendation": "One concrete research or positioning decision.",
  "claims": [
    {
      "id": "C1",
      "text": "The precise intended contribution",
      "central": true,
      "verdict": "risk",
      "reason": "Which part is covered and which exact distinction remains",
      "source_ids": ["S1"]
    }
  ],
  "sources": [
    {
      "id": "S1",
      "title": "Verified source title",
      "url": "https://example.org/original-source",
      "date": "Verified public date of this inspected version, or empty if unverified",
      "version": "The inspected containing version or release; state when unversioned",
      "evidence_level": "selected_full_text",
      "locator": "Actual section, theorem, equation, page, or file location",
      "finding": "What the inspected source establishes for the mapped claim",
      "difference": "The concrete remaining difference, or no material difference",
      "claim_ids": ["C1"],
      "excerpt": "Optional short exact source quotation"
    }
  ],
  "next_steps": ["A prioritized action tied to the finding"],
  "coverage": {
    "queries": [
      {"query": "An actual executed search query", "purpose": "Which claim/route it tested", "result": "What was found or why it failed"}
    ],
    "gaps": ["Only specific unfinished checks or access failures; use an empty array if none"]
  }
}
```

The object above illustrates the schema, not a real assessment. Replace every example value with actual evidence. Do not copy illustrative dates or URLs into reports. `verdict` is `safe`, `risk`, or `scooped`; `status: incomplete` uses top-level `verdict: null`. On an incomplete run, omit unassessed claims and keep supported partial claim judgments; name the unassessed work in `coverage.gaps` and the summary. `source_ids` and `claim_ids` must resolve within the same report and agree in both directions.

Set `language` explicitly in new reports. Follow the user's report-language preference; otherwise use the conversation language, with English as the fallback for languages other than English or Chinese. Write the title, summary, recommendation, claim explanations, evidence descriptions, next steps, and coverage explanations in the selected language. Preserve original source titles, exact quotations, URLs, dates, version identifiers, and executed query strings. Verdict, basis, and evidence-level identifiers stay unchanged.

Language selection is `--language en|zh-CN` first, then JSON `language`, then `zh-CN` for older JSON files without the field. Unsupported values are rejected. A CLI override changes interface labels only; it does not translate report content. To deliver both versions, prepare two JSON files with matching prose and render each to its own HTML file. Both use the same offline, responsive layout; no network translation or runtime language switch is required.

`basis` is `novelty` (current novelty) or `public_priority` (historical public priority). Infer it from the actual question and evidence, and name it in the chat verdict as well. For `public_priority`, record the verified user's public milestone as `user_milestone: {"date": "actual public date", "url": "original public URL", "description": "what matching content was public then"}`. A completed priority report requires this record. For an unpublished idea use `novelty` and `user_milestone: null`. When both questions are relevant, put the secondary finding explicitly in the summary/recommendation without changing the basis mid-report.

A completed report has central claims and actual search queries. `risk` and `scooped` claims cite their evidence. A risk claim needs at least a read abstract or stronger primary evidence with a usable HTTP(S) URL. A `scooped` claim cites inspected technical content (`selected_full_text`, `full_text`, or `released_artifact`) with a verified date, version, locator, and usable URL. The headline follows central claims exactly: all safe means `safe`; all scooped means `scooped`; otherwise `risk`. Peripheral statuses cannot change it. An incomplete report retains supported partial judgments and lists the decision-blocking evidence that is missing.

Include the closest meaningful competitors, not every search hit. A source record distinguishes what it establishes, its material difference, and how deeply it was read. Its URL, date, version, and locator all describe the same inspected version containing the relevant evidence. Pin versioned URLs where available. If multiple versions matter, record each separately; an earlier announcement/metadata record cannot backdate a result verified only in a later version. Source URLs use HTTP(S). Do not add fabricated risk percentages, invented confidence scores, or decorative metrics. Record the assessment time from the active session's date/time context, not model recollection.

Save the JSON and HTML in a new task output directory. Render with `scripts/render_report.py`; the helper refuses to overwrite an existing output, so choose a new filename when revising. Return a short in-chat decision with the central claim comparisons and source links, plus the HTML link; the reader must not have to open a file to discover the verdict. A screenshot of the actual rendered summary can supplement the chat summary when useful, but does not replace selectable text or evidence links. A mock/demo report must be prominently labeled as such and must not pretend to assess the user's real project.
