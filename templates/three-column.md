---
title: Three-Column Prompt (Purpose / Information / Control)
version: 1.0.0
owner: core
tags: [template, structure, building-blocks]
required_variables: [objective, input]
models_tested: []
---

# Purpose

>> components/roles/{{role}}.md

- Objective: {{objective}}
- Audience: {{audience}}

# Information

- Context: {{context}}
- Input:
{{input}}
- Sources: {{sources}}

>> components/examples/{{example_set}}.md

# Control

- Constraints: {{constraints}}

>> components/rules/{{safety}}.md
>> components/formats/{{format}}.md

## Success criteria

Complete the task only when all of the following are met:
{{success_criteria}}
