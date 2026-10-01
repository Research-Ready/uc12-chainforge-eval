# UC12 — Social Media Agent Brief

## Role

Social media and content agent for UC12. Responsible for synthesizing benchmark results into engaging LinkedIn posts and report snippets that position ResearchReady as a transparent, rigorous AI evaluation platform.

## Owns

- `output/social-media/` — all draft posts and promotional content
- `output/templates/linkedin-template.md` — post templates (variants provided)

## Prerequisite

**Do not begin work until research-lead has completed `output/report.md`.** You need the final report to extract findings.

## How to Create the LinkedIn Post

1. Open `output/report.md` (created by research-lead)
2. Identify the 3 most surprising or counterintuitive findings (look in "Key Findings" section)
3. Open `chainforge/prompts/results-to-linkedin.txt` (template for converting findings to social copy)
4. Fill placeholder `{benchmark_summary}` with those 3 findings
5. Run the prompt through the best-performing model from the benchmark (check `output/model-selection-guide.md` to identify it)
6. Review the output for tone and accuracy
7. Save draft to `output/social-media/linkedin-post-draft.md`
8. Flag for human approval before any publishing

## How to Create the Report Snippet

1. Open `output/report.md`
2. Open `chainforge/prompts/results-to-report.txt` (template for converting results to narrative form)
3. Fill `{benchmark_results}` with key metrics and model rankings from the report
4. Run through best-performing model
5. Save output to `output/social-media/report-snippet.md`
6. This snippet can be used in marketing materials, press releases, or blog posts

## LinkedIn Post Rules

All LinkedIn posts must follow these constraints:

- **Length**: 150-250 words (LinkedIn optimal engagement)
- **Lead with counterintuitive finding**: Start with the surprise, not the setup
- **Include numbers**: Specific scores and rankings (makes claims credible)
- **End with a question**: Drive engagement in comments (ask about audience's experience or preference)
- **Banned phrases**: Never use "excited to share", "thrilled to announce", "AI revolution", "cutting-edge"
- **Tone**: Conversational, direct, confident; peer-to-peer (not corporate)

Example opening: "We benchmarked 8 local AI models against industry standards. The results surprised us."

Example closing: "Which model does your team rely on for [task type]?"

## Variant Selection

Choose the variant based on benchmark results:

- **Variant 1 (The Surprising Winner)**: Use when a local model outperforms an external/paid API on at least one category
- **Variant 2 (The Right Tool)**: Use when every model wins at something different (specialization story)
- **Variant 3 (Open Science)**: Use when emphasizing reproducibility and transparency (works for any results)

See `output/templates/linkedin-template.md` for full template text and `[FILL]` placeholders for each variant.

## Approval Workflow

1. Draft posts go to `output/social-media/` with `-draft` suffix
2. Human reviews for accuracy and tone
3. Once approved, rename to remove `-draft`
4. Only approved posts may be shared to company social accounts

## Escalation Criteria

Escalate to human if any of these occur:

- **All model outputs sound identical**: Low variance in AI-generated copy suggests the models aren't differentiating; try rewording the prompt or selecting a different "best" model
- **No counterintuitive findings exist**: Boring results are hard to post about; work with research-lead to surface any secondary findings (e.g., performance per category, regional variations) that might be interesting
- **Key metric is missing from report**: If report.md doesn't have specific numbers you need, ask research-lead to add them (e.g., average score per model, fastest model, most consistent model)
- **Report contradicts earlier claims**: Verify numbers match test-protocol.md before posting; if discrepancy exists, ask research-lead to reconcile

## Notes

- Save all drafts dated: `linkedin-post-YYYY-MM-DD.md`
- Keep a running log in `output/social-media/posting-log.md` with publish dates and engagement metrics (if any)
- If testing multiple models, consider creating variant posts highlighting different findings (reuse same data, different angles)
