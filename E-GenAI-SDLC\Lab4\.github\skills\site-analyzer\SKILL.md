---
name: site-analyzer
description: 'Analyze a web page for SEO and availability basics. Use when you need to check: HTTP 200 response, favicon presence, page title (max 50 characters), and meta description (max 130 characters). Triggers: "analyze site", "check page", "SEO check", "validate URL", "site audit".'
argument-hint: '<URL to analyze>'
---

# Site Analyzer

Analyze a web page for essential SEO and health indicators.

## When to Use

- Validating a URL before launch or publication
- Quick SEO audit of a page's metadata
- Checking whether a site returns a healthy HTTP response

## Checks Performed

| Check | Criteria | Pass Condition |
|---|---|---|
| HTTP Response | Status code | Must be `200` |
| Favicon | `<link rel="icon">` or `/favicon.ico` | Must be present |
| Page Title | `<title>` tag content | Must exist and be ≤ 50 characters |
| Meta Description | `<meta name="description">` content | Must exist and be ≤ 130 characters |

## Procedure

1. **Receive the URL** from the user (e.g., `https://example.com`).
2. **Fetch the page** using the fetch/browser tool and record the HTTP status code.
3. **Check HTTP response**: verify the status code is `200`. Flag any other code (301, 404, 500, etc.) as a failure.
4. **Check favicon**:
   - Look for `<link rel="icon" ...>` or `<link rel="shortcut icon" ...>` in `<head>`.
   - If absent, also check whether `/favicon.ico` resolves (append to origin URL).
   - Report PASS or FAIL.
5. **Check title**:
   - Extract the text content of the `<title>` tag.
   - If missing → FAIL.
   - If present but longer than 50 characters → WARN (too long for optimal SEO display).
   - Otherwise → PASS. Report the actual character count.
6. **Check meta description**:
   - Extract the `content` attribute of `<meta name="description">`.
   - If missing → FAIL.
   - If present but longer than 130 characters → WARN (may be truncated in SERPs).
   - Otherwise → PASS. Report the actual character count.
7. **Summarize results** in a structured table (see Output Format below).

## Output Format

Present results as a Markdown table followed by a brief summary:

```
## Site Analysis: <URL>

| Check              | Status | Detail                              |
|--------------------|--------|-------------------------------------|
| HTTP Response      | ✅ PASS | 200 OK                              |
| Favicon            | ✅ PASS | Found via <link rel="icon">         |
| Title              | ⚠️ WARN | 63 chars (max 50): "My Very Long..." |
| Meta Description   | ✅ PASS | 98 chars                            |

### Summary
- 3 checks passed, 1 warning, 0 failures.
- Recommendation: Shorten the page title to 50 characters or fewer.
```

Status legend:
- ✅ **PASS** — criterion met
- ⚠️ **WARN** — present but exceeds recommended length
- ❌ **FAIL** — missing or HTTP error

## Decision Points

- If the page returns a non-200 status, note it and still attempt to parse any returned HTML (some servers return content with 4xx).
- If the page cannot be fetched at all, report all checks as FAIL with the network error.
- Relative favicon URLs (e.g., `/favicon.ico`) should be resolved against the page's origin.
