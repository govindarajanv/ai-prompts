---
title: Code Review Assistant
version: 1.0.0
owner: eng
tags: [coding, review, quality]
required_variables: [language, criteria]
models_tested: [gpt-4o]
---

>> components/roles/senior-engineer.md
>> components/rules/safety-accuracy.md

## Review request

Please review the following code against {{criteria}}. Focus on correctness, readability, and idiomatic use of the language. Provide a short verdict, a prioritized list of issues, and concrete suggested fixes with code snippets.

```{{language}}
{{code}}
```
