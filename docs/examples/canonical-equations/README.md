# Synthetic live smoke replay: canonical differential equations

This compact public example replays an archived synthetic live smoke test. It is not a paired with-skill/without-skill comparison, a held-out case, or a fresh literature search.

The exact user input is preserved in Chinese in [`prompt.txt`](prompt.txt). It names no paper, author, URL, or arXiv identifier. The model independently found the decisive original sources.

**English translation of the original Chinese prompt:** The proposed new method chooses a Feynman master-integral basis so that the dimensionally regulated differential equation becomes `d f = ε (Σ_i A_i d log W_i) f`, with constant matrices `A_i`, and then expands in `ε` to obtain iterated integrals. A massless one-loop box illustrates the method. The claimed innovation is the general solution strategy, not a complete result for a specific new topology. There is no public manuscript. Search and give a definite overlap verdict and report.

The run used `gpt-5.6-sol` with `high` reasoning on 2026-10-08.

## Archived result

**Verdict: `scooped` / 几乎已被 scoop.** The following is an English summary of the archived Chinese output.

The archived report found that [Henn 2013 v1](https://arxiv.org/pdf/1304.1806v1) already presented the general idea of choosing a basis to obtain an epsilon-factorized canonical system and solving it through iterated integrals. [Henn 2014 v1](https://arxiv.org/pdf/1412.2296v1) then gave the same kind of constant-matrix system and order-by-order solution for a massless one-loop on-shell box family. The earlier [1992 one-loop integral paper](https://arxiv.org/pdf/hep-ph/9212308v1) supported the narrower history of differential equations for the box example.

The recommended action was direct: do not present the general strategy or the one-loop box demonstration as a new method. A new claim would need a concrete technical increment, such as a new canonicalization algorithm with proved scope, a computable extension beyond multiple polylogarithms, or a complete result for a previously untreated topology.

## Files and limits

- [`report.json`](report.json) preserves the reviewed archived scientific content; its title marks the public synthetic replay.
- [English HTML report](report.en.html) and [English JSON](report.en.json) translate the archived assessment and use the English report interface. Verdicts, claim/source mappings, dates, URLs, version identifiers, and executed queries are preserved. This translation is not a new search run.
- [`report.html`](report.html) preserves the original Chinese rendering.
- [`provenance.json`](provenance.json) records the archived source hash, run settings, renderer inputs, and public-file hashes.

This example only shows that the workflow can recover a clear known-prior-work case from a no-reference prompt. It supports no statistical claim about accuracy, speed, or performance on unseen cases.
