# examples.md — Variation & Customization Guide

This file shows how every building block of a "good prompt" can be **varied and
customized** using this library's design. It walks through the 12 blocks from the
README's GOOD PROMPT framework.

**One consistent example is used throughout:** a *code review of a Python login
endpoint*, built from `templates/three-column.md`. Each block section shows the
part of that example it controls, and how to vary it for a different prompt.

## The two mechanisms your design gives you

Two composition features do all the work:

1. **Value substitution** — `{{var}}` becomes a value from a values file or `--var`.
2. **Variable-driven includes** — `>> components/path/{{var}}.md` picks *which*
   existing component file to inline.

The reference template `templates/three-column.md`:

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

## The consistent example: review this login endpoint

Values file `examples/review.values.yaml` (shipped in the repo):

```yaml
role: senior-engineer
tone: professional-precise
objective: Review the login endpoint for correctness, security, and testability
audience: The pull-request author
context: We are refactoring our Python FastAPI service to add rate limiting
input: |-
  @app.post("/login")
  def login(username: str, password: str):
      user = db.query(User).filter(User.name == username).first()
      if user and check_password(password, user.hash):
          return {"token": gen_token(user)}
      raise HTTPException(401, "bad credentials")
sources: https://example.com/style-guide, https://example.com/api-auth-cheatsheet
example_set: code-review
constraints: prioritize correctness over style; do not suggest unrelated refactors
safety: safety-accuracy
format: code-review
success_criteria: |-
  - A one-line verdict (APPROVE / REQUEST CHANGES / COMMENT)
  - Issues ordered by severity with locations
  - A concrete fix with code for each issue
  - No claims not supported by the shown code
```

Render it:

```bash
python3 bin/render.py templates/three-column.md --values examples/review.values.yaml
```

Output inlines every component and fills every slot. Below, each block shows how
to change **that one thing** to get a different prompt — always zero template edits.

---

## PURPOSE — why this prompt exists

### 1. Role — vary by include selection (`>> roles/{{role}}.md`)

`{{role}}` chooses *which* role file is inlined. In our example:

```yaml
role: senior-engineer   # → inlines components/roles/senior-engineer.md
```
produces:
> "You are a senior software engineer who writes clean, maintainable code..."

Swap the role and the whole persona changes:

```bash
python3 bin/render.py templates/three-column.md --values examples/review.values.yaml \
  --var role=data-analyst
```
Now the "review" is a data-correctness audit instead of a code review, with no
template change. Add any new role as one file under `components/roles/`.

### 2. Objective — vary by value

The objective is one-off prose, so it's a value:

```yaml
objective: Review the login endpoint for correctness, security, and testability
```
Override without a new file:
```bash
--var objective="Review only the security aspects of this endpoint"
```

### 3. Audience — vary by value

Audience sets how the review is pitched:
```yaml
audience: The pull-request author
```
```bash
--var audience="a junior developer new to FastAPI"
```

### 4. Tone — vary by include selection (`>> styles/{{tone}}.md`)

`{{tone}}` selects a voice file:
```yaml
tone: professional-precise   # → inlines components/styles/professional-precise.md
```
```bash
--var tone=friendly-clear
```
Add a voice once at `components/styles/<name>.md` and reuse it anywhere.

---

## INFORMATION — what the model needs to work with

### 5. Context — vary by value

Background is value prose:
```yaml
context: We are refactoring our Python FastAPI service to add rate limiting
```
```bash
--var context="This is a greenfield service about to launch; nothing is in prod yet"
```

### 6. Input — vary by value (multi-line)

Input is the code/data to process. Multi-line values use YAML block scalars or JSON:
```yaml
input: |-
  @app.post("/login")
  def login(username: str, password: str):
      ...
```
or the same as JSON:
```json
{ "input": "@app.post(\"/login\")\ndef login(...): ..." }
```
Change the input to review a *different* function and nothing else changes:
```bash
python3 bin/render.py templates/three-column.md --values examples/review.values.yaml \
  --var objective="Review this signup handler" \
  --var input="def signup(email: str):\n    ..."
```

### 7. Sources — vary by value

References/links are a value:
```yaml
sources: https://example.com/style-guide, https://example.com/api-auth-cheatsheet
```
```bash
--var sources="https://owasp.org/api-security, internal wiki: API patterns"
```

### 8. Examples — vary by include selection (`>> examples/{{example_set}}.md`)

Each few-shot set is a component file; `{{example_set}}` picks one:
```yaml
example_set: code-review   # → inlines components/examples/code-review.md
```
Add a new few-shot set as one file (e.g. `components/examples/security-review.md`)
and any review can adopt it via `example_set: security-review`.

---

## CONTROL — how the model must behave and produce

### 9. Constraints — vary by value or include

Constraints are usually short enough to be a value:
```yaml
constraints: prioritize correctness over style; do not suggest unrelated refactors
```
If a constraint set is reused everywhere, promote it to a file and select it via
include instead:
```markdown
>> components/rules/{{constraints}}.md
```
```yaml
constraints: constraints   # → inlines components/rules/constraints.md
```
You pick per block: one-off → value, shared → include. Both are supported.

### 10. Safety & Accuracy — vary by include selection (`>> rules/{{safety}}.md`)

Safety rules are shared standards, so they live as files:
```yaml
safety: safety-accuracy   # → inlines components/rules/safety-accuracy.md
```
Any review automatically carries the shared rules. Add a stricter set once
(`components/rules/safety-accuracy-strict.md`) and switch with
`safety: safety-accuracy-strict`.

### 11. Output Format — vary by include selection (`>> formats/{{format}}.md`)

Formats are shared structures:
```yaml
format: code-review   # → inlines components/formats/code-review.md
```
This example's format forces: Verdict → Issues → Fixes → Praise. Switching format
re-shapes the entire review:
```bash
python3 bin/render.py templates/three-column.md --values examples/review.values.yaml \
  --var objective="Summarize this endpoint for a release note" \
  --var input="login endpoint: verifies password, issues JWT" \
  --var format=exec-summary
```
Same template, now an executive summary instead of a review — only the format and
task changed.

### 12. Success Criteria — vary by value (multi-line checklist)

The completion checklist is a multi-line value:
```yaml
success_criteria: |-
  - A one-line verdict (APPROVE / REQUEST CHANGES / COMMENT)
  - Issues ordered by severity with locations
  - A concrete fix with code for each issue
  - No claims not supported by the shown code
```
For a standard, reused checklist, pull a shared component instead:
```markdown
>> components/formats/success-checklist.md
```

---

## Worked example: the same template, four different prompts

The base code-review example runs as shipped:

```bash
python3 bin/render.py templates/three-column.md --values examples/review.values.yaml
```

Change only **values** (or which component a variable selects) and you get a
completely different prompt with **zero** template edits. Here are four variations
of the exact same template:

```bash
# (1) As shipped — strict code review of the login endpoint
python3 bin/render.py templates/three-column.md --values examples/review.values.yaml

# (2) Same engineer role, but focus on security only, for a new input
python3 bin/render.py templates/three-column.md --values examples/review.values.yaml \
  --var objective="Review only the security aspects of this endpoint" \
  --var input="def signup(email: str):\n    ..." \
  --var sources="https://owasp.org/api-security"

# (3) Different role, tone, and output — a friendly summary for executives
python3 bin/render.py templates/three-column.md --values examples/review.values.yaml \
  --var role=data-analyst --var tone=friendly-clear \
  --var objective="Summarize the login endpoint for the exec team" \
  --var input="POST /login verifies the password and issues a JWT; rate limiting added" \
  --var format=exec-summary

# (4) Same template, a persuasive sales-writer task instead of a review
python3 bin/render.py templates/three-column.md --values examples/review.values.yaml \
  --var role=expert-writer --var tone=friendly-clear \
  --var objective="Write a cold email to re-engage a lapsed customer" \
  --var audience="Busy purchasing managers" \
  --var context="We sell an analytics platform the customer trialed 6 months ago" \
  --var input="Customer: Acme Corp; Contact: Priya (Head of Ops)" \
  --var example_set=sales-outreach --var format=exec-summary \
  --var constraints="under 150 words, no pushy language"
```

One template, four very different prompts — that is the payoff of values-driven
composability: the building blocks stay single-sourced (`components/`), and only
the per-invocation inputs and selected components change.

That is the composability model: **one template, many prompts**, produced by
varying per-block values and/or selecting different component files.

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
