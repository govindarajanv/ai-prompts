# Example: code review (few-shot)

## Weak review (before)
"The function is fine. Maybe add a comment. Could be more efficient."

## Good review (after)
"**Verdict: REQUEST CHANGES.**
1. **BLOCKER** — `gen_token(user)` is called before `user` is checked for `None`
   (login:4). A non-existent user is never checked, so this line raises
   `AttributeError` instead of returning 401. Move the lookup/validation earlier.
2. **NIT** — `username`/`password` are never type-annotated (login:3). Add
   `str` annotations and a `str` return type for clarity.
3. **PRAISE** — reusing the existing `check_password` helper keeps the flow simple."

## What changed
- Gave an instant verdict.
- Ordered issues by severity with exact locations.
- Paired each issue with a concrete fix.
- Kept praise brief and specific.
