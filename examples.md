# examples.md — Variation & Customization Guide

This file shows how every building block of a "good prompt" can be **varied and
customized** using this library's design. It walks through the 12 blocks from the
README's GOOD PROMPT framework, each with concrete examples.

## The two mechanisms your design gives you

Everything below uses just two composition features:

1. **Value substitution** — `{{var}}` becomes a value from a values file or `--var`.
2. **Variable-driven includes** — `>> components/path/{{var}}.md` picks *which*
   existing component file to inline.

The reference template is `templates/three-column.md`:

```markdown
# Purpose
>> components/roles/{{role}}.md
- Objective: {{objective}}
- Audience: {{audience}}

# Information
- Context: {{context}}
- Input: {{input}}
- Sources: {{sources}}
>> components/examples/{{example_set}}.md

# Control
- Constraints: {{constraints}}
>> components/rules/{{safety}}.md
>> components/formats/{{format}}.md
## Success criteria
{{success_criteria}}
```

Same template, many prompts. Below, each block shows how to vary it.

---

## PURPOSE

### 1. Role — vary by include selection

`{{role}}` selects *which* role file to inline. Add a file per role, then switch
with a value.

```
components/roles/
├── expert-writer.md
├── senior-engineer.md
└── data-analyst.md
```

```yaml
# values: role chooses the file
role: senior-engineer     # → inlines components/roles/senior-engineer.md
```
```bash
python3 bin/render.py templates/three-column.md --var role=data-analyst
```

**To add a new role** (one `components/roles/<name>.md`), since includes
look up `components/roles/<role>.md`:

```
components/roles/legal-reviewer.md   # written once, reusable everywhere
```
then `role: legal-reviewer` selects it.

### 2. Objective — vary by value

The objective is prose, so it's a plain value:
```yaml
objective: Write a persuasive cold email to re-engage a lapsed customer
```
Override per run without a new file:
```bash
--var objective="Summarize this PR for a release note"
```

### 3. Audience — vary by value

Audience changes tone/depth; it's a value:
```yaml
audience: Busy purchasing managers
```
```bash
--var audience="non-technical stakeholders"
```

### 4. Tone — vary by include selection

Like Role, `{{tone}}` selects a voice file:
```
components/styles/
├── friendly-clear.md
└── professional-precise.md
```
```yaml
tone: professional-precise     # → inlines components/styles/professional-precise.md
```
Add a new voice by dropping `components/styles/<name>.md` once.

---

## INFORMATION

### 5. Context — vary by value

Background is unmetered prose; a value:
```yaml
context: We sell an analytics platform the customer trialed 6 months ago
```

### 6. Input — vary by value (multi-line)

Input is often a code block, CSV, or document. Multi-line values work via JSON or
YAML block scalars:
```yaml
# YAML literal block
input: |-
  Customer: Acme Corp
  Contact: Priya (Head of Ops)
  Prior trial: used the dashboard for 2 weeks
```
or JSON for code:
```json
{ "input": "def fetch(url):\n    import requests\n    return requests.get(url).json()\n" }
```

### 7. Sources — vary by value

A list/links; a value:
```yaml
sources: https://example.com/pricing, https://example.com/case-studies
```

### 8. Examples — vary by include selection (few-shot)

Each few-shot set is a component file; `{{example_set}}` picks one:
```
components/examples/
└── sales-outreach.md
```
```yaml
example_set: sales-outreach   # → inlines components/examples/sales-outreach.md
```
Add a new few-shot set as one file and reuse it across many prompts.

---

## CONTROL

### 9. Constraints — vary by value or include

Constraints are usually short enough to be a value:
```yaml
constraints: under 150 words, no pushy language
```
But if you have a *standard, reused* constraint set, make it a component file and
select it via include, exactly like safety:
```
components/rules/constraints.md
```
```markdown
>> components/rules/{{constraints}}.md
```
with `constraints: constraints`. You choose per block whether the variation is
inline (value) or shared (include) — the design supports both.

### 10. Safety & Accuracy — vary by include selection

Safety rules are shared standards, so they live as files and are selected:
```
components/rules/
├── safety-accuracy.md
└── constraints.md
```
```yaml
safety: safety-accuracy   # → inlines components/rules/safety-accuracy.md
```

### 11. Output Format — vary by include selection

Formats are shared, reused structures; select one via `{{format}}`:
```
components/formats/
├── exec-summary.md
└── success-checklist.md
```
```yaml
format: exec-summary   # → inlines components/formats/exec-summary.md
```
Add a new format as one file (e.g. `components/formats/code-review.md`) and any
prompt can adopt it by setting `format: code-review`.

### 12. Success Criteria — vary by value (multi-line checklist)

A checklist; a multi-line value:
```yaml
success_criteria: |-
  - A clear subject line
  - One call to action
  - Personalization using the customer's name and context
  - No claims we cannot support
```
For *standard* criteria, reuse the shared checklist via an include instead:
```markdown
>> components/formats/success-checklist.md
```

---

## Worked example: the same template, four different prompts

The full 12-area example ships as `examples/full-prompt.values.yaml` and renders with:

```bash
python3 bin/render.py templates/three-column.md --values examples/full-prompt.values.yaml
```

Change one or two values and you get a different prompt with **zero** template edits:

```bash
# same role/style, different objective + audience + input
python3 bin/render.py templates/three-column.md \
  --values examples/full-prompt.values.yaml \
  --var role=data-analyst --var tone=professional-precise \
  --var objective="Summarize Q1 metrics for the exec team" \
  --var input="Q1 revenue up 12%, users up 8%, churn flat" \
  --var format=exec-summary
```

---

## Decisions: when to use value vs include

| Block | Prefer | Why |
|-------|--------|-----|
| Role (1) | include | Shared persona; reused across prompts |
| Tone (4) | include | Shared voice; reused across prompts |
| Examples (8) | include | Shared few-shot sets |
| Safety (10) | include | Shared rules; must be consistent |
| Output Format (11) | include | Shared structures |
| Objective (2) | value | One-off prose |
| Audience (3) | value | One-off |
| Context (5) | value | One-off background |
| Input (6) | value | The data/code being processed |
| Sources (7) | value | One-off links |
| Constraints (9) | either | Value for one-off; include for standard sets |
| Success Criteria (12) | either | Value for one-off; include for standard checklist |

**Rule of thumb:** if the same text is used by more than one prompt → make it a
component file and select via include. If it's specific to this one invocation →
make it a value. That single rule keeps everything DRY.
