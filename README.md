# AI Prompt Library

A simple, file-based system for managing a library of AI prompts. Prompts are plain
Markdown files versioned with Git, built from **reusable components**, filled with
**variables**, and composed into a ready-to-use prompt by a tiny local renderer.

Everything is free, open, local, and portable — no SaaS, no database, no heavy
platform. Works with any editor (Cursor, VS Code, Obsidian, Vim, ...) and any chat
app (ChatGPT, Claude, Gemini) via copy/paste.

---

## Why this design

The core tension in prompt libraries is **reuse** vs **simplicity**. We solve it
with three small ideas:

1. **Components are just files.** A role, a brand voice, a safety rule, an output
   format — each lives once in `components/` and is pulled into any prompt by a
   single `>> path` line.
2. **Variables are `{{placeholders}}`.** One template file serves many inputs.
3. **A 100-line renderer** inlines components and substitutes variables when you
   need a final, copy-paste-ready prompt. Nothing else is required.

---

## Directory layout

```
ai-prompts/
├── README.md               # this file
├── bin/
│   └── render.py           # optional renderer: inline + substitute + strip frontmatter
├── prompts/                # FINAL ready-to-use prompts, organized by domain
│   ├── writing/            #   e.g. blog-post.md
│   ├── coding/             #   e.g. code-review.md
│   └── analysis/           #   e.g. data-summary.md
├── components/             # REUSABLE pieces, defined once
│   ├── roles/              #   e.g. expert-writer.md, senior-engineer.md
│   ├── styles/             #   brand voice / tone (friendly-clear, professional-precise)
│   ├── rules/              #   safety, output, constraint rules
│   └── formats/            #   output format skeletons
├── templates/              # OPTIONAL skeletons for new prompts (with {{vars}})
└── examples/               # sample values files + rendered outputs
```

- **`prompts/`** — what you actually ship. Each file is standalone-readable and has
  YAML frontmatter for metadata.
- **`components/`** — the DRY heart. Sub-folders by *kind* (role, style, rule,
  format) so pieces are discoverable by purpose.
- **`templates/`** — starting points for authoring new prompts.
- **`examples/`** — sample `*.values.*` inputs and a place for rendered outputs.

---

## Conventions

### 1. Prompt files (in `prompts/`)

Every prompt is a Markdown file with optional YAML frontmatter:

```markdown
---
title: Friendly Blog Post Draft
version: 1.0.0
owner: writing-team
tags: [writing, blog, marketing]
required_variables: [topic, audience]
models_tested: [gpt-4o, claude-3-5-sonnet]
---

>> components/roles/expert-writer.md        # pull in a reusable role
>> components/styles/friendly-clear.md      # pull in brand voice
>> components/rules/output-conciseness.md  # pull in output rules

Audience: {{audience}}
Topic: {{topic}}

Write a blog post ...
```

Recommended frontmatter fields (all optional, feel free to extend):

| Field              | Purpose                                              |
|--------------------|------------------------------------------------------|
| `title`            | Human-readable name                                  |
| `version`          | Semantic version; bump on meaningful changes         |
| `owner`            | Team or person accountable                            |
| `tags`             | Discoverability (search/labels)                       |
| `required_variables`| Variables a caller must supply                       |
| `models_tested`    | Which models you validated against                   |

### 2. Includes: the DRY mechanism

A line that starts with `>>` at column 0 inlines the contents of another file:

```
>> components/roles/expert-writer.md
```

- Paths are **root-relative** (from the repo top) — so includes work the same no
  matter which sub-folder a prompt lives in. The prompt's own directory is tried as
  a fallback for local snippets.
- Includes are **recursive** (a component can include another) with cycle protection.
- Include paths are **variable-driven**: `>> components/roles/{{role}}.md` inlines the
  file named by the `role` value (e.g. `expert-writer` → `expert-writer.md`). This is
  what lets one template *compose different building blocks* per invocation, not just
  fill different values.
- Includes whose files are missing are left in place with a `<!-- missing -->` hint.
- Editor note: extensions like VS Code/Cursor are fine with these lines; the
  renderer turns them into real content at composition time.

### 3. Variables

Use `{{name}}` anywhere. They resolve from, in precedence order (lowest → highest):

1. a `--values` file (JSON or simple `key: value`),
2. `--var key=value` flags on the command line.

Undefined `{{placeholders}}` are left intact (and reported on stderr) so you can
fill them by hand or spot a mistake. This keeps templates safely reusable.

### 4. Versioning

- Each prompt file carries its own `version` in frontmatter — edit it when you
  iterate, following [semantic versioning](https://semver.org/).
- The whole library is Git-versioned naturally: `git log` is your full history,
  `git diff` shows exactly what changed in a prompt, and branches are how you
  prototype new prompts before promoting them.

---

## Tooling: `bin/render.py`

A single, dependency-free Python script (stdlib only) that turns a prompt file into
a final, copy-paste-ready prompt:

```bash
# Compose with a values file + overrides
python3 bin/render.py prompts/writing/blog-post.md \
    --values examples/blog.values.yaml \
    --var topic="Getting Started with Docker"

# Compose with multi-line JSON values (great for code/data blocks)
python3 bin/render.py prompts/coding/code-review.md \
    --values examples/code-review.values.json

# Keep the YAML frontmatter (opt-out of stripping)
python3 bin/render.py prompts/writing/blog-post.md --keep-frontmatter

# See which variables are still undefined
python3 bin/render.py prompts/writing/blog-post.md 1>/dev/null
#   --> <!-- unfilled variables: audience, topic -->
```

What it does:

1. **Strips YAML frontmatter** by default (so the output is clean to paste),
   unless `--keep-frontmatter`.
2. **Inlines all `>>` includes** recursively. Include paths may themselves contain
   `{{variables}}` — e.g. `>> components/roles/{{role}}.md` — so a single template
   can select *which* component to inline based on the values supplied.
3. **Substitutes `{{variables}}`** from the values file and CLI flags. Values files
   support JSON, simple `key: value` lines, and YAML block scalars (`|-`/`>-`) for
   multi-line inputs like code or data.
4. **Prints to stdout** — redirect to `rendered/` or pipe into a pager/clipboard.

Because output goes to stdout, it's trivial to build on later: write to a file,
feed it to a CLI, paste it into a chat app, or trigger it from an editor save hook.
Rendered files go under `rendered/` (git-ignored).

### Why a script at all?

The system works fine without it — you can read a prompt file, open an include, and
paste. The renderer just removes the tedium (and any chance of inconsistency) when
you want a finished, single-block prompt. It's deliberately tiny (< 100 lines) and
easily replaced by whatever you prefer (a shell script, an Obsidian plugin, a Cursor
command).

---

## Workflow

**To use a prompt:**
1. Open the prompt file in `prompts/<domain>/`.
2. `python3 bin/render.py <file> --values examples/<name>.values.yaml` (or add
   `--var` values inline).
3. Copy the output into your chat app — or read the file directly and fill
   `{{placeholders}}` by hand if you don't want to run anything.

**To create a new prompt:**
1. Copy a `templates/*.md` skeleton into `prompts/<domain>/`.
2. Add `>> components/...` lines for any role/style/rule you want to reuse.
3. Fill in `{{variables}}` and frontmatter metadata.
4. If a piece is genuinely new (a voice, a rule, a format), add it to
   `components/` **once** and reuse it everywhere — that's the DRY win.

**To collaborate via Git:** edit files, open branches for experiments, review diffs
of prompt changes, and merge. Metadata lives in the files, so there's no sync to a
remote service.

---

## Extensibility

This is the minimum that works well today; it's structured to grow:

- **New piece types** → add a sub-folder under `components/` (e.g.
  `components/few_shot/`, `components/constraints/`).
- **A CLI** → `bin/render.py` already reads stdin/stdout-style args; add glob
  rendering, linting of frontmatter, or validation of required variables.
- **Editor integration** → a VS Code/Cursor task or Obsidian Templater hook that
  runs `render.py` on save.
- **Search/index** → `grep` or a tiny script over frontmatter `tags`/`title`.

All storage is plain files, so any tool you add later operates on plain text.

---

## Requirements

- Python 3.8+ (only for the optional renderer; the files themselves need nothing).
- Any text editor, and git for history.

No other dependencies, no accounts, no network calls.
