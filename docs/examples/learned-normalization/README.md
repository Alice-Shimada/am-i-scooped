# Historical replay: learned normalization before 2016-08-01

This public example shows how claim structure can change a research-overlap verdict. It replays one archived calibration case; it is not a new literature search.

The exact user input is preserved in Chinese in [`prompt.txt`](prompt.txt). It names no paper, author, URL, arXiv identifier, or method title. It only describes mini-batch statistics, per-sample layer statistics, and learned weights that combine their means and variances. Both archived runs independently found the original papers.

## Input

**English translation of the original Chinese prompt:** Search public literature through 2016-08-01. The proposed method has two parts: use mini-batch and per-sample layer statistics as candidate normalizers, then learn separate combination weights for their means and variances in every normalization layer so the layer adapts to batch size. There is no public manuscript. Judge the known and still-distinct parts separately and give an overall verdict.

Both arms ran on 2026-10-08 with `gpt-5.6-sol` and `high` reasoning. The historical literature cutoff was 2016-08-01.

## Archived comparison

| Arm | Archived verdict | English summary of the archived output |
|---|---|---|
| Without the skill (baseline) | `risk` / 已有风险 | BN and LN already supplied the two candidate statistics. No pre-cutoff source was found that learned their mean and variance mixing weights; the baseline nevertheless treated the known candidates as an independently threatened part of the claim. |
| With the revised skill | `safe` / 目前安全 | BN and LN were recorded as known peripheral components. The central claim remained the joint mechanism: compute both statistics in one layer and learn how to combine each pair. Neither inspected pre-cutoff paper established that mechanism. |

The research facts agree across the two arms:

- [Batch Normalization v1](https://arxiv.org/html/1502.03167v1) used mini-batch statistics before the cutoff.
- [Layer Normalization v1](https://arxiv.org/html/1607.06450v1) used per-sample layer statistics before the cutoff and discussed batch-size behavior.
- Neither inspected pre-cutoff source learned a joint BN/LN weighting inside one normalization layer.
- The baseline also found [Switchable Normalization](https://arxiv.org/abs/1806.10779), published after the cutoff, as a later direct learned-mixture construction.

The verdict changed because the revised workflow preserves the relation between known components. It treats “compute both candidates and learn their joint weighting” as the central proposition, while still marking the BN and LN ingredients themselves as already known. The baseline split the prompt more aggressively and promoted the known ingredients into a separate threatened contribution.

## Read the artifacts

- [`baseline.json`](baseline.json) is the complete B11 baseline entry, including its original evidence records and queries.
- [`report.json`](report.json) is the archived revised-workflow report, with only the title labeled as a historical replay.
- [`report.html`](report.html) is the offline rendering of that report. The report remains in Chinese because it preserves the archived runtime output.
- [`provenance.json`](provenance.json) records run settings and SHA-256 hashes for the archived sources and published files.

This is a calibration-case illustration produced after workflow revisions. It is not held-out performance evidence and supports no statistical claim about accuracy or speed. The replay does not establish exhaustive coverage beyond the archived search and 2016-08-01 cutoff.
