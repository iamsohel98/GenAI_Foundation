---
name: interview-prep
description: 'Generate interview preparation questions for a specific role and experience level. Use when the user asks for interview prep, technical interview questions, behavioural interview questions, behavioral interview questions, role-based interview practice, or practice questions using Role and Number of years.'
argument-hint: '<Role> | <Number of years>'
---

# Interview Prep

Generate targeted interview preparation questions for a candidate based on the supplied role and years of experience.

## Inputs

- **Role**: Job title or target position, such as `Java Developer`, `Data Engineer`, `QA Automation Engineer`, or `Frontend Developer`.
- **Number of years**: Candidate experience level, such as `2`, `5`, or `8` years.

If either input is missing, ask the user for the missing value before generating questions.

## Experience Calibration

- **0-2 years**: Focus on fundamentals, basic implementation, debugging, collaboration, and learning mindset.
- **3-5 years**: Include practical design decisions, production troubleshooting, code quality, ownership, and cross-team work.
- **6-9 years**: Emphasize architecture, scaling, reliability, mentoring, tradeoffs, and leading initiatives.
- **10+ years**: Focus on technical strategy, system-wide judgment, stakeholder alignment, leadership, risk management, and long-term maintainability.

## Procedure

1. Parse the supplied arguments into `Role` and `Number of years`.
2. Calibrate question difficulty using the experience ranges above.
3. Generate exactly **5 technical interview questions** for the role and experience level.
4. Generate exactly **5 behavioural interview questions** for the same role and experience level.
5. Keep questions specific, practical, and interview-ready.
6. Avoid generic questions that could apply to any role unless they are tailored with role-specific context.

## Output Format

Use this structure:

```markdown
## Interview Prep: <Role> (<Number of years> years)

### Technical Questions
1. ...
2. ...
3. ...
4. ...
5. ...

### Behavioural Questions
1. ...
2. ...
3. ...
4. ...
5. ...
```

## Quality Checks

- Output contains exactly 5 technical questions.
- Output contains exactly 5 behavioural questions.
- Questions match the supplied role.
- Difficulty matches the supplied number of years.
- No answers are included unless the user explicitly asks for answers.