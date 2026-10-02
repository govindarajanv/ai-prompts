#!/usr/bin/env python3
"""render.py — compose a final AI prompt from a prompt file.

Features:
  * Inline components/pieces: a line beginning with ">> path" is replaced
    by the contents of that file (recursively allowed, cycle-safe).
  * Variable substitution of {{name}} placeholders. Variables come from,
    in order of precedence (lowest to highest):
      1. a --values file (YAML-ish "key: value" or JSON)
      2. --var key=value CLI flags
  * Leaves any undefined {{placeholders}} intact so you can paste-fill by hand.
  * Strips YAML frontmatter (--- ... ---) from output so the final prompt is
    clean and ready to copy/paste.

Usage:
  python3 bin/render.py prompts/writing/blog-post.md \
      --values examples/blog.values.yaml --var topic=Gardening --var audience=beginners
"""
import argparse
import json
import re
import sys
from pathlib import Path

FRONTMATTER = re.compile(r"\A---\s*\n.*?\n---\s*\n", re.DOTALL)
VARIABLE = re.compile(r"\{\{\s*([a-zA-Z0-9_.-]+)\s*\}\}")
INCLUDE = re.compile(r"^\s*>>\s*(\S+)\s*$", re.MULTILINE)


class CycleError(Exception):
    pass


def find_root(start_dir):
    """Walk up from a directory to find the repo root (dir containing a .git/ or components/)."""
    cur = start_dir.resolve()
    for _ in range(20):
        if (cur / ".git").exists() or (cur / "components").exists():
            return cur
        if cur.parent == cur:
            break
        cur = cur.parent
    return start_dir.resolve()


def load_values(path):
    """Load a values file; supports JSON or simple 'key: value' lines.

    Also folds YAML block scalars: a value of ``|-`` (literal block) or
    ``>-`` (folded block) collects the indented lines that follow it.
    """
    if path is None:
        return {}
    text = Path(path).read_text()
    text = text.strip()
    if not text:
        return {}
    if text.startswith("{"):
        data = json.loads(text)
        return data if isinstance(data, dict) else {}

    values = {}
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].split("#", 1)[0].rstrip()
        if not line or ":" not in line:
            i += 1
            continue
        key_raw, _, val_raw = line.partition(":")
        key = key_raw.strip()
        val = val_raw.strip().strip("'\"")
        # YAML literal/folded block scalar
        if val in ("|-", ">-"):
            collect = []
            i += 1
            while i < len(lines) and lines[i][:1] in (" ", "\t"):
                collect.append(lines[i].lstrip())
                i += 1
            body = "\n".join(collect)
            values[key] = body if val == "|-" else " ".join(body.split())
            continue
        values[key] = val
        i += 1
    return values


def resolve_include(rel, prompt_dir, root_dir):
    """Resolve an include path: prefer repo-root-relative, fall back to prompt-dir-relative."""
    for base in (root_dir, prompt_dir):
        candidate = (base / rel).resolve()
        for allowed in (root_dir.resolve(), prompt_dir.resolve()):
            try:
                candidate.relative_to(allowed)
            except ValueError:
                continue
            if candidate.exists():
                return candidate
    return (root_dir / rel).resolve()  # for consistent missing-reporting


def expand_includes(text, prompt_dir, root_dir, values, seen, depth=0):
    """Recursively inline '>> path' includes. Returns (resolved_text, missing)."""
    if depth > 50:
        raise CycleError("include nesting too deep (possible cycle)")

    missing = []

    def repl(match):
        rel = match.group(1)
        # Substitute {{variables}} inside the include path so a values file can
        # choose which component to inline (e.g. ">> styles/{{tone}}.md").
        rel = substitute(rel, values)
        target = resolve_include(rel, prompt_dir, root_dir)
        if not target.exists():
            missing.append(rel)
            return f">> {rel}  <!-- missing -->"
        if str(target) in seen:
            raise CycleError(f"include cycle at '{rel}'")
        content = target.read_text()
        resolved, sub_missing = expand_includes(
            content, target.parent, root_dir, values,
            seen | {str(target)}, depth + 1
        )
        missing.extend(sub_missing)
        return resolved

    text, n = INCLUDE.subn(repl, text)
    if n == 0:
        return text, missing
    if n and depth < 50:
        text, more = expand_includes(text, prompt_dir, root_dir, values, seen, depth + 1)
        missing.extend(more)
    return text, missing


def substitute(text, values):
    def repl(match):
        key = match.group(1)
        if key in values:
            return str(values[key])
        return match.group(0)  # leave undefined intact

    return VARIABLE.sub(repl, text)


def main():
    parser = argparse.ArgumentParser(description="Compose an AI prompt file.")
    parser.add_argument("prompt", help="Path to the prompt file (e.g. prompts/writing/blog-post.md)")
    parser.add_argument("--values", help="Path to a values file (JSON or key: value)")
    parser.add_argument("--var", action="append", default=[], metavar="KEY=VALUE",
                        help="Set a variable (repeatable)")
    parser.add_argument("--keep-frontmatter", action="store_true",
                        help="Keep YAML frontmatter in output")
    args = parser.parse_args()

    prompt_path = Path(args.prompt)
    if not prompt_path.exists():
        print(f"error: file not found: {prompt_path}", file=sys.stderr)
        sys.exit(1)

    prompt_dir = prompt_path.parent
    root_dir = find_root(prompt_dir)
    text = prompt_path.read_text()

    file_values = load_values(args.values)
    values = dict(file_values)
    for item in args.var:
        if "=" not in item:
            print(f"error: --var expects KEY=VALUE, got '{item}'", file=sys.stderr)
            sys.exit(1)
        k, _, v = item.partition("=")
        values[k.strip()] = v

    if not args.keep_frontmatter:
        text = FRONTMATTER.sub("", text, count=1)

    text, _ = expand_includes(text, prompt_dir, root_dir, values, {str(prompt_path)})
    text = substitute(text, values).strip() + "\n"

    undefined = sorted(set(VARIABLE.findall(text)))
    print(text)
    if undefined:
        print(f"\n<!-- unfilled variables: {', '.join(undefined)} -->",
              file=sys.stderr)


if __name__ == "__main__":
    main()
