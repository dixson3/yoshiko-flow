# ML010 CriticMarkup fixture

This fixture deliberately contains bare CriticMarkup constructs (REQ-MDLINT-006).

An addition {++inserted text++} in prose.
A deletion {--removed text--} in prose.
A substitution {~~old~>new~~} in prose.
A highlight {==marked text==} in prose.
A comment {>>editor note<<} in prose.

Exempt in an inline-code span: `{++not flagged++}` stays clean.

A brace pair with no separator {~~no arrow here~~} is NOT a substitution and is
not flagged.

Exempt in a fenced code block:

```text
{++also not flagged++}
{~~old~>new~~}
```
