# Evidence and judgment

## What counts as overlap

Compare the target result as a logical claim: objects, hypotheses, domain, output, and strength. Different words or algorithms can express the same claim. A broader result covers the user's target only when its assumptions allow the user's case and its conclusion implies the user's result; show that mapping. An application to a new domain can be significant, but do not infer significance from a changed example alone.

Keep these questions separate:

- **Result:** Did they actually establish the claimed output, or just propose it?
- **Method:** Is the procedure the same, an independently useful alternative, or merely renamed?
- **Scope:** Do dimensions, regimes, input classes, assumptions, and precision match?
- **Completeness:** Is there a proved/general result, finite numerical check, partial implementation, or future-work statement?
- **Time:** When was the matching content public, and which version contains it?

Use specific language: “Their theorem covers C1 under the same hypotheses; C2's nonplanar case is excluded by assumption A” is useful. “The topics are similar but differences may remain” is not.

## Avoid false alarms from claim splitting

The unit of novelty is the user's proposition, including its relations, quantifiers, and scope—not a bag of ingredients. “Train this new architecture for node classification” does not claim the first node classifier. “Combine known statistics with a learned mixing rule” does not claim discovery of each statistic. Keep such a contribution together unless the user independently advertises its components as separate inventions.

For a combination claim, list the **integration step** and show whether an actual prior source establishes it. Multiple papers separately containing the components do not establish that combination. For a scope extension, show whether the old theorem/algorithm actually implies the new case; a restricted predecessor need not threaten the new generalization. Put necessary citations to background work in the report without turning them into a yellow headline.

This does not grant novelty to arbitrary recombinations. If the supposedly new integration is only notation, packaging, a stated motivation, or an implementation change while the operative method/result is unchanged, explain that equivalence and classify accordingly. If the user separately claims two first results and one is already covered, retain the mixed `risk` judgment. A threat explanation must identify the advertised novelty it removes, not merely count familiar components.

## Verdict thresholds

**Safe:** Search all central claims through multiple formulations and inspect the closest credible candidates. Explain the checked difference or the absence of a same-result candidate in the searched scope. Do not require a proof that no prior work exists; do require an actual search and candidate scrutiny. An inaccessible decisive source blocks a safe verdict. A failed query, empty tool response, or abstract that omits a detail is not evidence that the detail is absent.

**Risk:** There is a named, evidenced threat: coverage of a separately advertised proposition-level output or capability, a closely matching concrete announced result, or substantial overlap with one main claim while another remains distinct. Partial coverage means an actual promised novel output/capability is covered; overlap with ingredients or a task name alone does not qualify. Cite at least a read abstract, relevant primary text, or inspected released artifact with a usable public URL; metadata and unverified user excerpts alone do not establish a public threat. Explain exactly why it is not yet `scooped` (e.g. one independently claimed kinematic regime is already solved, a public announcement supplies no derivation, or v1/v2 priority remains unchecked). Do not assign risk merely because the research area is active or because a source failed to load.

**Scooped:** Technical content already covers the core promised contribution with matching or weaker assumptions, and the chronology supports prior public availability. Cite the actual statement/calculation/artifact and version. A different implementation, language, package wrapper, or workflow alone does not preserve result novelty. If an independently valuable method or extension remains, identify it directly without using it to hide coverage of the original claim.

Identify the central novelty claims from the user's stated purpose, not to engineer a preferred outcome. Standard background tools are not central innovations unless the user actually claims them as such. Derive the overall verdict exactly from central claims: all `safe` means `safe`; all `scooped` means `scooped`; otherwise `risk`. Thus one covered central claim does not erase another surviving central contribution, and a peripheral overlap cannot turn an otherwise safe project yellow. Report peripheral findings separately.

Declare the basis before classifying: `novelty` compares an intended contribution with work public by the assessment date; `public_priority` compares verified public disclosures. Infer the basis from the actual question and supplied record. For historical priority, a later duplicate does not scoop an earlier user disclosure: a `safe` priority verdict must identify the matching content and both dates. Report the current competitive overlap separately rather than pretending it is absent. Conversely, an earlier user disclosure does not make an already known result novel today. If the user only has an unpublished idea today, existing public completion defeats its proposed first-result claim. Do not invent a historical user milestone when none was supplied; ask for it only if the historical priority question requires it.

## Evidence levels and dates

- `metadata`: bibliographic discovery only.
- `abstract`: enough to flag a precise overlap; normally not enough to certify technical coverage or a decisive exclusion.
- `selected_full_text`: inspected the relevant technical passages; record sections/equations/pages and what they establish.
- `full_text`: reserve for actually reading the whole paper.
- `released_artifact`: inspected the relevant authoritative released code, dataset, or technical result, pinned to its actual release/commit and contents.
- `user_excerpt`: supplied material whose original context/authenticity has not been independently checked.

Use short exact quotations only when they help verify a decisive claim, within the active source quotation limits. Prefer precise paraphrases plus a real locator. Each source record's date, URL, version, and locator describe the same inspected containing version. Earlier and later versions may have separate records under the same work when priority requires comparison. State the earliest verified availability, not an unverified first appearance. An earlier metadata-only or announcement-only record cannot backdate a later technical result. For mutable repositories, pin a relevant commit/release and inspect its contents; creation dates and recent activity do not establish when a feature existed. An announcement can establish that a claim was public at that time without establishing that the claimed science was completed.

For PDF locations, distinguish printed page numbers from PDF page positions. Tool indices such as `P0` are zero-based; report one-based PDF positions or explicitly label printed page numbers, alongside the verified equation/section.

## Theoretical physics comparisons

For amplitudes and Feynman integrals, preserve distinctions that often decide the result:

- Loop order, multiplicity, topology/family, planarity, masses, external virtualities, color/helicity, and exact kinematics.
- An integrand, cut, master basis, canonical DE, symbol/alphabet, boundary constants, and integrated amplitude are different deliverables.
- A numerical point, finite-field sample, recognized constant candidate, and exact symbolic result have different strength.
- A worked family is different from a reusable algorithm; an existing package is different from the modified workflow actually used.
- Match normalization, regulator order, boundary conditions, analytic region, and completeness of sectors before claiming one result covers another.

Apply only relevant distinctions; this is not a checklist the user must fill out.
